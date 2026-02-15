# import os
# from tavily import TavilyClient
# from dotenv import load_dotenv
# from pathlib import Path
# import json

# load_dotenv()
# TVLY_API_KEY = os.getenv("TAVILY_API_KEY", "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")
# url = "https://www.tesla.com/"
# instruction = "Find any pages that will help us understand the company's offering, customers, market, positioning, buyers, maturity, motion, momentum, compliance, integrability, and readiness."
# tavily_client = TavilyClient(api_key=TVLY_API_KEY)

# response = tavily_client.crawl(
#     url = url,
#     instructions=instruction,
#     max_depth=1,
#     max_breadth=50,
#     extract_depth="advanced"
# )
# path = Path("../playground/tesla.json")
# path.parent.mkdir(parents=True, exist_ok=True)
# path.write_text(json.dumps(response, indent=2), encoding="utf-8")

# for item in response.get("results", []):
#     if item.get("raw_content"):
#         page_url = item.get("url", url)
#         response[page_url] = {
#             'raw_content': item.get('raw_content'),
#             'source': 'company_website'
#         }


from typing import List, Any, cast, Dict, TypedDict
import json


class CompanyProduct():
    name: str
    description: str


class TargetMarkets():
    industries: List[str]
    ideal_customer_profile: str


class SalesTriggers():
    recent_funding_or_news: str
    strategic_priorities: str


class ImpactMetrics():
    case_study: str
    result: str


class SalesIntelligence():
    green_flags: List[str]
    red_flags: List[str]
    compliance_standards: List[str]


class Persona(TypedDict):
    company_name: str
    industry: str
    hq_location: str
    mission_statement: str
    core_products: List[CompanyProduct]
    target_markets: TargetMarkets
    sales_triggers: SalesTriggers
    impact_metrics: List[ImpactMetrics]
    sales_intelligence: SalesIntelligence


def _parse_persona_response(data) -> Persona:
    """Parse LLM JSON response into Persona TypedDict."""
    # ---- core_products ----
    core_products: List[Dict[str, str]] = []
    for product in data.get("core_products", []) or []:
        if isinstance(product, dict):
            core_products.append({
                "name": str(product.get("name", "")),
                "description": str(product.get("description", "")),
            })
        elif isinstance(product, str):
            core_products.append({"name": product, "description": ""})

    # ---- target_market (NOTE: singular in your JSON) ----
    target_market = data.get("target_market", {})
    if isinstance(target_market, str):
        target_market = {"industries": [],
                         "ideal_customer_profile": target_market}
    elif not isinstance(target_market, dict):
        target_market = {}

    # ---- sales_triggers ----
    sales_triggers = data.get("sales_triggers", {})
    if isinstance(sales_triggers, str):
        sales_triggers = {"recent_news": sales_triggers,
                          "strategic_priorities": ""}
    elif not isinstance(sales_triggers, dict):
        sales_triggers = {}

    # Map your JSON keys to the keys your Persona expects
    recent_news = sales_triggers.get(
        "recent_news") or sales_triggers.get("recent_funding_or_news", "")
    strategic_priorities = sales_triggers.get(
        "strategic_priorities") or sales_triggers.get("strategic_priorities_2025_2026", "")

    # ---- sales_intelligence ----
    sales_intelligence = data.get("sales_intelligence", {})
    if isinstance(sales_intelligence, str):
        sales_intelligence = {"green_flags": [],
                              "red_flags": [], "compliance_standards": []}
    elif not isinstance(sales_intelligence, dict):
        sales_intelligence = {}

    # ---- impact_metrics (safe) ----
    impact_metrics: List[Dict[str, Any]] = []
    for metric in data.get("impact_metrics", []) or []:
        if isinstance(metric, dict):
            impact_metrics.append({
                "case_study": metric.get("case_study", ""),
                "result": metric.get("result", ""),
            })

    persona: Persona = cast(Persona, {
        "company_name": data.get("company_name", data.get("company", "Unknown")),
        "industry": data.get("industry", "Unknown"),
        "hq_location": data.get("hq_location", "Unknown"),
        "mission_statement": data.get("mission_statement", data.get("executive_summary", "")),
        "core_products": core_products,
        "target_markets": cast(Dict[str, Any], {
            "industries": target_market.get("industries", []),
            "ideal_customer_profile": target_market.get("ideal_customer_profile", ""),
        }),
        "sales_triggers": cast(Dict[str, Any], {
            "recent_news": recent_news,
            "strategic_priorities": strategic_priorities,
        }),
        "impact_metrics": cast(List[Dict[str, Any]], impact_metrics),
        "sales_intelligence": cast(Dict[str, Any], {
            "green_flags": sales_intelligence.get("green_flags", []),
            "red_flags": sales_intelligence.get("red_flags", []),
            "compliance_standards": sales_intelligence.get("compliance_standards", []),
        }),
    })

    return persona


with open('../storage/personas/Snorkel_interim.json', 'r') as fi:
    data = json.load(fi)


persona = _parse_persona_response(data)
print(persona)
