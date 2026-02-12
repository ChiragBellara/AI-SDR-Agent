"""
Run the full research workflow (grounding → researchers → collector → curator).
Usage from project root:
  uv run python -m src.run_workflow
  uv run python -m src.run_workflow --company "Acme" --url "https://acme.com" --industry "SaaS"
"""
import argparse
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

from graph import Graph
from logger.universal_logger import setup_logger

logger = setup_logger("AI_SDR.RunWorkflow")
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "storage" / "personas"


def parse_args():
    p = argparse.ArgumentParser(description="Run the full AI-SDR research workflow")
    p.add_argument("--company", default="Snorkel", help="Company name")
    p.add_argument("--url", default="https://snorkel.ai/", help="Company URL")
    p.add_argument("--hq", default="California", help="HQ location")
    p.add_argument("--industry", default="Enterprise AI", help="Industry")
    p.add_argument("--out", default=None, help="Output JSON path (default: storage/personas/<company>_workflow.json)")
    return p.parse_args()


async def main():
    load_dotenv()
    args = parse_args()
    graph = Graph(
        company=args.company,
        url=args.url,
        hq_location=args.hq,
        industry=args.industry,
    )
    thread = {"configurable": {"thread_id": "run-workflow-1"}}
    final_state = None
    logger.info("Starting workflow: grounding → researchers → collector → curator")
    async for state in graph.run(thread):
        final_state = state
        # Optional: log each step (keys that were updated)
        logger.debug("Step: %s", list(state.keys()) if isinstance(state, dict) else state)
    if final_state is None:
        logger.warning("Workflow produced no state")
        return
    out_path = Path(args.out) if args.out else OUTPUT_DIR / f"{args.company}_workflow.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Build JSON-serializable output (skip messages and other non-serializable fields)
    def to_serializable(obj):
        if isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_serializable(v) for v in obj]
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        return str(obj)
    payload = to_serializable(final_state)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Workflow finished. Output: %s", out_path)


if __name__ == "__main__":
    asyncio.run(main())
