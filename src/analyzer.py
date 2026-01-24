import os
import json
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel
from schema.LeadCard import LeadCard

LEAD_CARD_DIR = Path("../storage/identities")


class RankedItem(BaseModel):
    company_name: str
    fit_score_0_to_100: int
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


def call_llm_json(system: str, user_obj: Dict[str, Any]) -> str | None:
    provider, client = llm_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_obj)}
        ],
        temperature=0.2,
    )
    print(resp)
    return resp.choices[0].message.content


def rank_companies(goal: str, cards: List[LeadCard]) -> RankResult:
    system = (
        "You are an AI-SDR lead qualification agent. "
        "Given LeadCards for multiple companies, rank them for a sales goal. "
        "Return STRICT JSON only."
    )

    user = {
        "sales_goal": goal,
        "lead_cards": [c.model_dump() for c in cards],
        "output_schema": RankResult.model_json_schema(),
        "instructions": [
            "Rank all companies from best to worst fit for the sales_goal.",
            "fit_score_0_to_100 must be 0-100.",
            "reason must be 1-2 sentences and cite specific LeadCard signals (fields/phrases).",
            "Return JSON only with top-level key 'ranked'."
        ]
    }

    raw = call_llm_json(system, user)
    if raw:
        data = json.loads(strip_fences(raw))
        return RankResult.model_validate(data)

    raise RuntimeError("Cannot get the Ranked result.")
