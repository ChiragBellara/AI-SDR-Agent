OUTPUT_STRUCT = {
    "company_name": "string",
    "industry": "string",
    "mission_statement": "string",
    "core_products": [
        {
            "name": "string",
            "description": "string"
        }
    ],
    "target_market": {
        "industries": ["string"],
        "ideal_customer_profile": "string"
    },
    "sales_triggers": {
        "recent_funding_or_news": "string",
        "strategic_priorities": "string"
    },
    "impact_metrics": [
        {
            "case_study": "string",
            "result": "string"
        }
    ],
    "sales_intelligence": {
        "green_flags": ["string"],
        "red_flags": ["string"],
        "compliance_standards": ["string"]
    }
}


def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)
