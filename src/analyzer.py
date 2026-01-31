import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

from schema.LeadCard import LeadCard
from logger.llm_logger import _log_llm_call
from logger.universal_logger import setup_logger
from utils.prompts import RANK_COMPANIES_SYSTEM_PROMPT, RANK_COMPANIES_USER_INSTRUCTION

LEAD_CARD_DIR = Path("../storage/identities")
logger = setup_logger('AI_SDR.Analyzer')


class RankedItem(BaseModel):
    company_name: str
    fit_score_0_to_100: int
    is_competitor: bool = False
    top_outreach_roles: list[str] = []
    reason: str


class RankResult(BaseModel):
    ranked: List[RankedItem]


def strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[-1]
    if s.endswith("```"):
        s = s.rsplit("```", 1)[0]
    return s.strip()


def lead_card_path(company_name: str) -> Path:
    return LEAD_CARD_DIR / f"{company_name}.json"


def get_or_create_lead_card(p: Path) -> LeadCard:
    raw_data = p.read_text(encoding="utf-8")
    if raw_data:
        return LeadCard.model_validate_json(raw_data)
    raise RuntimeError("Company does not exist.")


def llm_client():
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        from openai import OpenAI
        return ("openai", OpenAI(api_key=openai_key))

    raise RuntimeError("Set OPENAI_API_KEY")


def call_llm_json(system: str, user_obj: Dict[str, Any], stage: str) -> str | None:
    provider, client = llm_client()
    model = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")
    start = time.perf_counter()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_obj)}
        ],
        # temperature=0.9,
    )
    latency_ms = (time.perf_counter() - start) * 1000
    usage = resp.usage
    _log_llm_call(stage=stage, provider=provider, model=model,
                  prompt_tokens=usage.prompt_tokens if usage else None,
                  completion_tokens=usage.completion_tokens if usage else None,
                  latency_ms=latency_ms,)

    return resp.choices[0].message.content


def rank_companies(goal: str, cards: List[LeadCard]) -> RankResult:
    system = RANK_COMPANIES_SYSTEM_PROMPT
    user = {
        "sales_goal": goal,
        "lead_cards": [c.model_dump() for c in cards],
        "output_schema": RankResult.model_json_schema(),
        "instructions": RANK_COMPANIES_USER_INSTRUCTION
    }

    raw = call_llm_json(system, user, "lead_ranking")
    if raw:
        data = json.loads(strip_fences(raw))
        return RankResult.model_validate(data)

    raise RuntimeError("Cannot get the Ranked result.")
