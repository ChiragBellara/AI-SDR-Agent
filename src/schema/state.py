from typing import TypedDict, Required, NotRequired, List, Dict, Any

class InputState(TypedDict, total=False):
    company: Required[str]
    company_url: NotRequired[str]
    hq_location: NotRequired[str]
    industry: NotRequired[str]

class ResearchState(InputState):
    site_scrape: Dict[str, Any]
    messages: List[Any]
    news_data: Dict[str, Any]
    trigger_data: Dict[str, Any]
    offering_data: Dict[str, Any]
    customer_data: Dict[str, Any]
    readiness_data: Dict[str, Any]
    company_briefing: str
    references: List[str]
    briefings: Dict[str, Any]
    report: str