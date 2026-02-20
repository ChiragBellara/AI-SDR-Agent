from typing import TypedDict, Required, NotRequired, List, Dict, Any


class InputState(TypedDict):
    company: Required[str]
    company_url: NotRequired[str]
    hq_location: NotRequired[str]
    industry: NotRequired[str]


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
    persona: NotRequired[Persona]
