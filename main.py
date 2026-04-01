import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from backend.graph import Graph
from backend.src.logger.universal_logger import setup_logger
from backend.src.schema.state import job_status
from backend.src.utils.json_utils import to_serializable

logger = setup_logger(__name__)

app = FastAPI(title="Sales Development Research API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    company: str
    company_url: str | None = None
    industry: str | None = None
    hq_location: str | None = None


@app.options("/research")
async def preflight():
    response = JSONResponse(content=None, status_code=200)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.post("/research")
async def research(data: ResearchRequest):
    try:
        logger.info(f"Received research request for {data.company}")
        job_id = str(uuid.uuid4())
        # ensure entry exists so stream/status readers see "pending"
        job_status[job_id]

        # kick off research in background — return job_id immediately
        asyncio.create_task(process_research(job_id, data))

        return JSONResponse(
            content={"job_id": job_id, "status": "started"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
        )

    except Exception as e:
        logger.error(f"Error initiating research: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


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

            # send any new events that have queued up
            while sent_index < len(events):
                event = events[sent_index]
                yield f"data: {json.dumps(event)}\n\n"
                sent_index += 1

            job_state = status.get("status")

            if job_state == "completed":
                persona = status.get("report")
                yield f"data: {json.dumps({'type': 'done', 'persona': persona})}\n\n"
                break

            if job_state == "failed":
                yield f"data: {json.dumps({'type': 'error', 'message': status.get('error', 'Research failed')})}\n\n"
                break

            await asyncio.sleep(0.3)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


async def process_research(job_id: str, data: ResearchRequest):
    """Run the research graph and push progress events into job_status."""
    def push(event: dict):
        job_status[job_id]["events"].append(event)

    try:
        logger.info(f"Starting research for {data.company}")

        push({"type": "progress", "step": "Initializing", "message": f"Starting research for {data.company}…"})

        graph = Graph(
            company=data.company,
            url=data.company_url or "",
            industry=data.industry or "",
            hq_location=data.hq_location or "",
            job_id=job_id
        )

        # Map LangGraph node names → human-readable labels
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

            label_active, label_done = node_labels.get(node_name, (node_name, node_name))

            # surface doc counts for research nodes when available
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

            push({"type": "node_done", "node": node_name, "message": f"{label_done}{detail}"})

            job_status[job_id].update({
                "status": "processing",
                "current_step": node_name,
                "last_update": datetime.now().isoformat(),
            })

        persona_content = to_serializable(final_state["persona"]["final_persona"]) or {}

        if persona_content:
            logger.info(f"Research completed for {data.company}")

            # Write persona to a JSON file for inspection and sharing
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            safe_name = data.company.lower().replace(" ", "_")
            output_path = output_dir / f"{safe_name}_{job_id[:8]}.json"
            output_path.write_text(
                json.dumps(persona_content, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            logger.info(f"Persona saved to {output_path}")
            job_status[job_id].update({
                "status": "completed",
                "report": persona_content,
                "company": data.company,
                "last_update": datetime.now().isoformat(),
            })
        else:
            logger.error(f"Research completed without persona. State keys: {list(final_state.keys())}")
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


@app.get("/")
async def ping():
    return {"message": "Alive"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
