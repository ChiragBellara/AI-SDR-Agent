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
    curated_news_data: Dict[str, Any]
    curated_trigger_data: Dict[str, Any]
    curated_offering_data: Dict[str, Any]
    curated_customer_data: Dict[str, Any]
    curated_readiness_data: Dict[str, Any]
    references: List[str]
    reference_titles: Dict[str, Any]
    reference_info: Dict[str, Any]
    report: str