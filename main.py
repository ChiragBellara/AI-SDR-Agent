import asyncio
import uuid
from datetime import datetime
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.graph import Graph
from backend.src.logger.universal_logger import setup_logger
from backend.src.schema.state import job_status
from backend.src.utils.json_utils import to_serializable

env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

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

        persona_content = await process_research(job_id, data)

        if job_status[job_id].get("status") == "failed":
            raise HTTPException(
                status_code=500,
                detail=job_status[job_id].get("error", "Research failed"),
            )

        response = JSONResponse(content={
            "status": "completed",
            "job_id": job_id,
            "persona_content": persona_content,
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating research: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def process_research(job_id: str, data: ResearchRequest):
    """Process research request asynchronously and store results"""
    try:
        await asyncio.sleep(0.5)

        logger.info(f"Starting research for {data.company}")

        graph = Graph(
            company=data.company,
            url=data.company_url or "",
            industry=data.industry or "",
            hq_location=data.hq_location or "",
            job_id=job_id
        )

        final_state = {}

        # Stream through the graph and update progress
        async for state in graph.run(thread={}):
            final_state.update(state)
            node_name = list(state.keys())[0] if state else 'unknown'
            logger.debug(f"Node completed: {node_name}")

            # Update job status with current step
            job_status[job_id].update({
                "status": "processing",
                "current_step": node_name,
                "last_update": datetime.now().isoformat()
            })

        # Extract final report
        persona_content = to_serializable(final_state["persona"]) or {}

        if persona_content:
            logger.info(
                f"Research completed. Report length: {len(persona_content)}")

            job_status[job_id].update({
                "status": "completed",
                "report": persona_content,
                "company": data.company,
                "last_update": datetime.now().isoformat()
            })  # type: ignore[arg-type]

            logger.info(f"Research completed successfully for {data.company}")
        else:
            logger.error(
                f"Research completed without report. State keys: {list(final_state.keys())}")
            job_status[job_id].update({
                "status": "failed",
                "error": "No report generated",
                "last_update": datetime.now().isoformat()
            })

        return persona_content

    except Exception as e:
        logger.error(f"Research failed: {str(e)}", exc_info=True)
        job_status[job_id].update({
            "status": "failed",
            "error": str(e),
            "last_update": datetime.now().isoformat()
        })


@app.get("/")
async def ping():
    return {"message": "Alive"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
