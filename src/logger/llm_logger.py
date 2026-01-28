# Used to log the stats of the LLM calls for the purpose of in-app monitoring
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


LOG_DIR = Path("../logs/")
today = datetime.today().strftime('%Y-%m-%d')


def _log_llm_call(
    *,
    stage: str,
    provider: str,
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
    latency_ms: float,
    extra: Dict[str, Any] | None = None,
):
    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stage": stage,
        "provider": provider,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": (
            (prompt_tokens or 0) + (completion_tokens or 0)
            if prompt_tokens is not None and completion_tokens is not None
            else None
        ),
        "latency_ms": round(latency_ms, 2),
    }

    if extra:
        record["extra"] = extra

    log_path = LOG_DIR / f"llm_calls_{today}.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
