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
    },
    "buyer_roles": [
        {
            "title": "string — specific job title e.g. VP of Engineering",
            "department": "string — e.g. Engineering, Revenue Operations",
            "daily_pain_points": ["string — specific, role-level problem they face day to day"],
            "success_metrics": ["string — what they are measured on e.g. deployment frequency, pipeline velocity"],
            "typical_objections": ["string — barriers they raise when considering new tools"]
        }
    ],
    "outbound_hooks": [
        {
            "hook_type": "string — one of: hiring | product_launch | funding | partnership | press | expansion",
            "specific_signal": "string — the concrete, recent event or observation that triggered this hook",
            "why_now": "string — why this signal makes NOW the right time to reach out",
            "source_or_evidence": "string — where this signal was found e.g. job posting, press release, news article"
        }
    ],
    "buyer_messaging": [
        {
            "role_title": "string — must match a title in buyer_roles",
            "value_prop": "string — why this buyer should care, framed around their specific pain",
            "pain_to_solution": "string — one sentence bridging their daily pain to the solution",
            "expected_outcome": "string — measurable result this buyer would experience",
            "opening_hook": "string — first line of a cold email or call opener, specific and conversational"
        }
    ]
}


def to_serializable(obj):
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)
