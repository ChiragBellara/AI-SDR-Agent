import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, ValidationError


class SourceEntry(BaseModel):
    name: str
    url: HttpUrl


def validate_sources(data):
    """Checks if the uploaded list matches our expected schema."""
    if not isinstance(data, list):
        return False, "Data must be a JSON list of objects."

    try:
        # Validate each item in the list
        validated_data = [SourceEntry(**item) for item in data]
        return True, validated_data
    except ValidationError as e:
        # Extract the specific error for the UI
        error_msg = f"Invalid format in entry: {e.errors()[0]['loc']} - {e.errors()[0]['msg']}"
        return False, error_msg
    except Exception as e:
        return False, str(e)


def _parse_first_json(raw: str) -> Optional[dict]:
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].strip()
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0].strip()

    if raw.startswith("["):
        arr = json.loads(raw)
        if not arr:
            return None
        return arr[0] if isinstance(arr[0], dict) else None

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(raw)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _merge_lead_cards(cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}

    scalar_fields = ["company_name", "category", "one_liner"]
    for f in scalar_fields:
        for c in cards:
            v = c.get(f)
            if v:
                merged[f] = v
                break
        merged.setdefault(f, None)

    list_fields = [
        "products_or_platform",
        "target_customers",
        "core_workflows",
        "technical_surface_area",
        "integrations_or_stack_hints",
        "compliance_or_regulatory_signals",
        "scale_and_growth_signals",
        "common_pain_points",
        "buyer_roles",
        "notable_keywords",
        "source_notes",
    ]

    for f in list_fields:
        seen = set()
        out = []
        for c in cards:
            vals = c.get(f) or []
            if isinstance(vals, list):
                for item in vals:
                    s = str(item).strip()
                    if s and s.lower() not in seen:
                        seen.add(s.lower())
                        out.append(s)
        merged[f] = out

    return merged
