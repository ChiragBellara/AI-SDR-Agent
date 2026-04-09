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


SELLER_BRIEF_STRUCT = {
    "fit_assessment": {
        "fit_level": "string — one of: Strong | Moderate | Weak",
        "rationale": "string — 1-2 sentences explaining why this product fits (or doesn't) this company right now",
        "strongest_connection": "string — the single sharpest overlap between the product and a live signal or pain. If fit_level is Weak, describe the closest available connection even if it is thin."
    },
    "lead_angle": {
        "entry_point": "string — the specific company pain or trigger that maps most directly to this product",
        "why_this_first": "string — why this angle beats other possible entry points"
    },
    "positioning": {
        "frame": "string — how to describe this product in the company's own language, not generic product marketing",
        "against_priorities": "string — how the product maps to the company's stated strategic priorities",
        "differentiator_to_lead_with": "string — which product differentiator resonates most given this company's context"
    },
    "objection_map": [
        {
            "red_flag": "string — the original red flag from the company persona verbatim",
            "how_to_handle": "string — specific response using the seller's product strengths",
            "reframe": "string — how to flip this into a discovery question or proof point"
        }
    ],
    "outreach_templates": {
        "email_subject": "string — personalized subject line, under 8 words. Set to null if fit_level is Weak.",
        "email_opener": "string — first 2 sentences of a cold email, specific and non-generic, referencing a real signal. Set to null if fit_level is Weak.",
        "call_opener": "string — spoken first line of a cold call, conversational tone, max 2 sentences. Set to null if fit_level is Weak."
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
