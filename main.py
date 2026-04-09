import asyncio
import json
import os
import re
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from backend.graph import Graph
from backend.src.logger.universal_logger import setup_logger
from backend.src.schema.state import job_status
from backend.src.utils.json_utils import SELLER_BRIEF_STRUCT, to_serializable
from backend.src.utils.prompts import SELLER_BRIEF_PROMPT

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Persona cache  (company+url → persona, keyed for 60-minute reuse)
# ---------------------------------------------------------------------------
CACHE_TTL_SECONDS = 60 * 60  # 60 minutes

# key → {"persona": dict, "cached_at": ISO str}
_persona_cache: dict[str, dict] = {}


def _cache_key(company: str, company_url: str | None) -> str:
    return f"{company.lower().strip()}|{(company_url or '').lower().strip()}"


def _get_cached(company: str, company_url: str | None) -> dict | None:
    entry = _persona_cache.get(_cache_key(company, company_url))
    if not entry:
        return None
    age = (datetime.now() -
           datetime.fromisoformat(entry["cached_at"])).total_seconds()
    if age > CACHE_TTL_SECONDS:
        _persona_cache.pop(_cache_key(company, company_url), None)
        return None
    return entry


def _set_cached(company: str, company_url: str | None, persona: dict) -> str:
    cached_at = datetime.now().isoformat()
    _persona_cache[_cache_key(company, company_url)] = {
        "persona": persona,
        "cached_at": cached_at,
    }
    return cached_at


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(title="Sales Development Research API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

allowed_origin = os.getenv("ALLOWED_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
)

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(_API_KEY_HEADER)):
    expected = os.getenv("APP_API_KEY")
    if not expected:
        # No key configured — allow all (useful for local dev without the var set)
        return
    if api_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


# ---------------------------------------------------------------------------
# Request schema
# ---------------------------------------------------------------------------
class ResearchRequest(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    company_url: str | None = Field(default=None, max_length=500)
    industry: str | None = Field(default=None, max_length=100)
    hq_location: str | None = Field(default=None, max_length=100)

    @field_validator("company_url")
    @classmethod
    def validate_url(cls, v: str | None) -> str | None:
        if v:
            parsed = urlparse(v)
            if parsed.scheme not in ("http", "https"):
                raise ValueError("URL must start with http:// or https://")
        return v


class SellerBriefRequest(BaseModel):
    product_name: str = Field(min_length=1, max_length=200)
    product_description: str = Field(min_length=1, max_length=1000)
    target_industries: str | None = Field(default=None, max_length=300)
    differentiators: str | None = Field(default=None, max_length=500)
    company_persona: dict  # Full PersonaConent JSON from the frontend


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def ping():
    return {"message": "Alive"}


@app.post("/research", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/hour")
async def research(request: Request, data: ResearchRequest):
    try:
        logger.info(f"Received research request for {data.company}")
        job_id = str(uuid.uuid4())
        # ensure entry exists so stream readers see "pending"
        job_status[job_id]
        asyncio.create_task(process_research(job_id, data))
        return JSONResponse(content={"job_id": job_id, "status": "started"})
    except Exception as e:
        logger.error(f"Error initiating research: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to start research. Please try again.")


@app.post("/seller-brief", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/hour")
async def seller_brief(request: Request, data: SellerBriefRequest):
    """Single LLM call that cross-references the seller's product with the company persona."""
    try:
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise HTTPException(status_code=500, detail="LLM not configured.")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=gemini_key,
            max_retries=0,
        )

        formatted_prompt = SELLER_BRIEF_PROMPT.format(
            seller_product=data.product_name,
            seller_description=data.product_description,
            target_industries=data.target_industries or "Not specified",
            differentiators=data.differentiators or "Not specified",
            company_persona=json.dumps(data.company_persona, indent=2),
            output_structure=json.dumps(SELLER_BRIEF_STRUCT, indent=2),
            year="2025-2026",
        )

        chain = llm | StrOutputParser()
        response = await chain.ainvoke(formatted_prompt)

        # Strip markdown code fences if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]

        brief = json.loads(response.strip())
        return JSONResponse(content={"seller_brief": brief})

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse seller brief JSON: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to generate seller brief. Please try again.")
    except Exception as e:
        logger.error(f"Seller brief error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to generate seller brief. Please try again.")


@app.get("/research/{job_id}/stream")
async def stream_research(job_id: str):
    """SSE endpoint — streams progress events then the final persona."""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")

    async def event_generator():
        sent_index = 0
        while True:
            status = job_status[job_id]
            events = status.get("events", [])

            while sent_index < len(events):
                event = events[sent_index]
                yield f"data: {json.dumps(event)}\n\n"
                sent_index += 1

            job_state = status.get("status")

            if job_state == "completed":
                persona = status.get("report")
                done_event: dict = {"type": "done", "persona": persona}
                if status.get("cache_hit"):
                    done_event["cache_hit"] = True
                    done_event["cached_at"] = status.get("cached_at")
                yield f"data: {json.dumps(done_event)}\n\n"
                break

            if job_state == "failed":
                yield f"data: {json.dumps({'type': 'error', 'message': 'Research failed. Please try again.'})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Background research job
# ---------------------------------------------------------------------------
async def process_research(job_id: str, data: ResearchRequest):
    """Run the research graph and push progress events into job_status."""
    def push(event: dict):
        job_status[job_id]["events"].append(event)

    try:
        logger.info(f"Starting research for {data.company}")

        # Check cache before running the full pipeline
        cached = _get_cached(data.company, data.company_url)
        if cached:
            logger.info(f"Cache hit for {data.company} — skipping pipeline")
            push({"type": "node_done", "node": "cache",
                 "message": "Loaded from cache"})
            job_status[job_id].update({
                "status": "completed",
                "report": cached["persona"],
                "company": data.company,
                "cache_hit": True,
                "cached_at": cached["cached_at"],
                "last_update": datetime.now().isoformat(),
            })
            return

        push({"type": "progress", "step": "Initializing",
             "message": f"Starting research for {data.company}…"})

        graph = Graph(
            company=data.company,
            url=data.company_url or "",
            industry=data.industry or "",
            hq_location=data.hq_location or "",
            job_id=job_id
        )

        node_labels = {
            "grounding":            ("Crawling website",        "Crawled company website"),
            "triggers_researcher":  ("Scanning sales triggers", "Scanned sales triggers"),
            "offering_researcher":  ("Analyzing offerings",     "Analyzed product offerings"),
            "readiness_researcher": ("Checking B2B readiness",  "Checked B2B readiness"),
            "customer_researcher":  ("Profiling customers",     "Profiled customer segments"),
            "news_analyst":         ("Gathering news",          "Gathered recent news"),
            "collector":            ("Aggregating research",    "Research aggregated"),
            "persona":              ("Synthesizing persona",    "Persona synthesized"),
        }

        final_state = {}

        async for state in graph.run(thread={}):
            final_state.update(state)
            node_name = list(state.keys())[0] if state else "unknown"

            label_active, label_done = node_labels.get(
                node_name, (node_name, node_name))

            detail = ""
            data_key_map = {
                "triggers_researcher":  "trigger_data",
                "offering_researcher":  "offering_data",
                "readiness_researcher": "readiness_data",
                "customer_researcher":  "customer_data",
                "news_analyst":         "news_data",
            }
            if dk := data_key_map.get(node_name):
                docs = final_state.get(dk, {})
                if docs:
                    detail = f" — {len(docs)} documents found"

            push({"type": "node_done", "node": node_name,
                 "message": f"{label_done}{detail}"})

            job_status[job_id].update({
                "status": "processing",
                "current_step": node_name,
                "last_update": datetime.now().isoformat(),
            })

        persona_content = to_serializable(
            final_state["persona"]["final_persona"]) or {}

        if persona_content:
            logger.info(f"Research completed for {data.company}")

            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            safe_name = re.sub(r"[^\w\-]", "_", data.company.lower())
            output_path = (
                output_dir / f"{safe_name}_{job_id[:8]}.json").resolve()
            # Guard against path traversal
            if not str(output_path).startswith(str(output_dir.resolve())):
                raise ValueError("Invalid output path")
            output_path.write_text(
                json.dumps(persona_content, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            logger.info(f"Persona saved to {output_path}")
            cached_at = _set_cached(
                data.company, data.company_url, persona_content)
            job_status[job_id].update({
                "status": "completed",
                "report": persona_content,
                "company": data.company,
                "cached_at": cached_at,
                "last_update": datetime.now().isoformat(),
            })
        else:
            logger.error(
                f"Research completed without persona. State keys: {list(final_state.keys())}")
            job_status[job_id].update({
                "status": "failed",
                "error": "No persona generated",
                "last_update": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Research failed: {str(e)}", exc_info=True)
        job_status[job_id].update({
            "status": "failed",
            "error": str(e),
            "last_update": datetime.now().isoformat(),
        })


# ---------------------------------------------------------------------------
# Startup: background job cleanup
# ---------------------------------------------------------------------------
async def _cleanup_old_jobs():
    """Remove completed/failed jobs older than 2 hours to prevent memory leaks."""
    while True:
        await asyncio.sleep(3600)
        cutoff = datetime.now() - timedelta(hours=2)
        to_delete = [
            jid for jid, data in list(job_status.items())
            if data.get("status") in ("completed", "failed")
            and datetime.fromisoformat(
                data.get("last_update", datetime.now().isoformat())
            ) < cutoff
        ]
        for jid in to_delete:
            del job_status[jid]
        if to_delete:
            logger.info(f"Cleaned up {len(to_delete)} old jobs")

        # Also evict expired cache entries
        expired_keys = [
            k for k, v in list(_persona_cache.items())
            if (datetime.now() - datetime.fromisoformat(v["cached_at"])).total_seconds() > CACHE_TTL_SECONDS
        ]
        for k in expired_keys:
            _persona_cache.pop(k, None)
        if expired_keys:
            logger.info(f"Evicted {len(expired_keys)} expired cache entries")


@app.on_event("startup")
async def startup():
    asyncio.create_task(_cleanup_old_jobs())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WEB_CONCURRENCY", 1))
    uvicorn.run("main:app", host="0.0.0.0", port=port,
                reload=False, workers=workers)
