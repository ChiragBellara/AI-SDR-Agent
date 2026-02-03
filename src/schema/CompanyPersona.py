from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict


# -------------------------
# Enums
# -------------------------

class FitTier(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class ProductType(str, Enum):
    software = "software"
    hardware = "hardware"
    platform = "platform"
    service = "service"


class PricingMotion(str, Enum):
    self_serve = "self-serve"
    sales_led = "sales-led"
    hybrid = "hybrid"


class PricingModel(str, Enum):
    per_seat = "per-seat"
    usage = "usage"
    per_asset = "per-asset"
    tiered = "tiered"
    unknown = "unknown"


class LegalReadiness(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CTAPrimary(str, Enum):
    request_demo = "request-demo"
    talk_to_sales = "talk-to-sales"
    get_started = "get-started"


class ApiMaturity(str, Enum):
    none = "none"
    basic = "basic"
    mature = "mature"
    unknown = "unknown"


class HookRelevance(str, Enum):
    pain = "pain"
    timing = "timing"
    roi = "roi"
    trust = "trust"
    integration = "integration"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class HighSignalPageType(str, Enum):
    products = "products"
    solutions = "solutions"
    customers = "customers"
    pricing = "pricing"
    security = "security"
    integrations = "integrations"
    industries = "industries"
    careers = "careers"


# -------------------------
# Sub-models
# -------------------------

class Domains(BaseModel):
    """Information about the Company's Online domains"""
    primary: str = ""
    subdomains_seen: List[str] = Field(default_factory=list)


class HQ(BaseModel):
    """Information about the Company Headquarters"""
    city: str = ""
    region: str = ""
    country: str = ""


class CompanyDescription(BaseModel):
    """General information about the Company"""
    one_liner: str = ""
    positioning: str = ""
    category: str = ""
    keywords: List[str] = Field(default_factory=list)


class LastFundingRound(BaseModel):
    """Information about the company's funding. Especially useful in cases of a startup."""
    type: str = ""
    date: str = ""  # keep as string if coming from scraped sources; can normalize later
    amount_usd: Optional[float] = None
    investors: List[str] = Field(default_factory=list)


class StageAndSize(BaseModel):
    """Information about the Company's size and strcuture."""
    employee_range: str = ""
    revenue_range: str = ""
    funding_stage: str = ""
    last_funding_round: LastFundingRound = Field(default_factory=LastFundingRound)
    public_company: bool = False
    ticker: str = ""


class Company(BaseModel):
    """Establish context and credibility of the company"""
    name: str = ""
    legal_name: str = ""
    website: str=""
    domains: Domains = Field(default_factory=Domains)
    hq: HQ = Field(default_factory=HQ)
    geo_coverage: List[str] = Field(default_factory=list)
    description: CompanyDescription = Field(default_factory=CompanyDescription)
    stage_and_size: StageAndSize = Field(default_factory=StageAndSize)


class FitRationale(BaseModel):
    """Rationale behind why the LLM thinks this comapny is someone the SDR should contact."""
    strong_signals: List[str] = Field(default_factory=list)
    weak_signals: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)


class TargetSegments(BaseModel):
    """What segments within the company are the best targets for our product."""
    customer_size: List[str] = Field(default_factory=lambda: ["SMB", "mid-market", "enterprise"])
    industries_served: List[str] = Field(default_factory=list)
    regions_served: List[str] = Field(default_factory=list)


class IcpFit(BaseModel):
    """Information about the company's fit for our product"""
    fit_score: int = 0
    fit_tier: FitTier = FitTier.C
    fit_rationale: FitRationale = Field(default_factory=FitRationale)
    target_segments: TargetSegments = Field(default_factory=TargetSegments)


class PrimaryProduct(BaseModel):
    """Information about the Company's Primary Offering"""
    name: str = ""
    type: ProductType = ProductType.software
    category: str = ""
    who_uses_it: List[str] = Field(default_factory=list)
    key_capabilities: List[str] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    differentiators: List[str] = Field(default_factory=list)
    pricing_motion: PricingMotion = PricingMotion.sales_led
    url_sources: List[HttpUrl] = Field(default_factory=list)


class PlatformSignals(BaseModel):
    """Information about the Company's Platform"""
    api_available: bool = False
    developer_docs_url: str = ""
    integration_marketplace_url: str = ""
    security_trust_url: str = ""


class ProductsAndOffering(BaseModel):
    """Information about the other products/services the Company offers"""
    primary_products: List[PrimaryProduct] = Field(default_factory=list)
    platform_signals: PlatformSignals = Field(default_factory=PlatformSignals)


class WhoTheySellTo(BaseModel):
    """Information about the Company's primary customers"""
    buyer_roles: List[str] = Field(default_factory=list)
    user_roles: List[str] = Field(default_factory=list)
    economic_buyer_roles: List[str] = Field(default_factory=list)
    typical_deal_triggers: List[str] = Field(default_factory=list)


class CustomerExample(BaseModel):
    """Structured information about the company's customers"""
    name: str = ""
    industry: str = ""
    size_hint: str = ""
    use_case: str = ""
    outcomes: List[str] = Field(default_factory=list)
    proof_url: str = ""


class LogoTierSummary(BaseModel):
    """Information about the company's Budget and procurement maturity"""
    enterprise_logos_present: bool = False
    notable_logos: List[str] = Field(default_factory=list)


class CustomerProfile(BaseModel):
    who_they_sell_to: WhoTheySellTo = Field(default_factory=WhoTheySellTo)
    industries: List[str] = Field(default_factory=list)
    customer_examples: List[CustomerExample] = Field(default_factory=list)
    logo_tier_summary: LogoTierSummary = Field(default_factory=LogoTierSummary)


class ValueMetrics(BaseModel):
    cost: List[str] = Field(default_factory=list)
    time: List[str] = Field(default_factory=list)
    risk: List[str] = Field(default_factory=list)
    revenue: List[str] = Field(default_factory=list)


class UrgencySignals(BaseModel):
    regulatory_pressure: List[str] = Field(default_factory=list)
    safety_pressure: List[str] = Field(default_factory=list)
    downtime_pressure: List[str] = Field(default_factory=list)
    scale_pressure: List[str] = Field(default_factory=list)


class PainPointsAndUseCases(BaseModel):
    stated_problems: List[str] = Field(default_factory=list)
    use_cases: List[str] = Field(default_factory=list)
    job_to_be_done: str = ""
    value_metrics: ValueMetrics = Field(default_factory=ValueMetrics)
    urgency_signals: UrgencySignals = Field(default_factory=UrgencySignals)


class Pricing(BaseModel):
    has_pricing_page: bool = False
    pricing_url: str = ""
    pricing_model: PricingModel = PricingModel.unknown
    starts_at_usd: Optional[float] = None
    enterprise_plan_present: bool = False
    quote_required: bool = False


class ProcurementSignals(BaseModel):
    security_certifications: List[str] = Field(default_factory=list)
    compliance_standards: List[str] = Field(default_factory=list)
    sso_saml_supported: Optional[bool] = None
    data_residency_options: List[str] = Field(default_factory=list)
    legal_readiness: LegalReadiness = LegalReadiness.medium


class SalesMotion(BaseModel):
    cta_primary: CTAPrimary = CTAPrimary.request_demo
    demo_required: bool = False
    trial_available: Optional[bool] = None


class BudgetAndBuying(BaseModel):
    pricing: Pricing = Field(default_factory=Pricing)
    procurement_signals: ProcurementSignals = Field(default_factory=ProcurementSignals)
    sales_motion: SalesMotion = Field(default_factory=SalesMotion)


class InferredStack(BaseModel):
    frontend: List[str] = Field(default_factory=list)
    backend: List[str] = Field(default_factory=list)
    cloud: List[str] = Field(default_factory=list)
    data: List[str] = Field(default_factory=list)
    observability: List[str] = Field(default_factory=list)


class IntegrationsAndEcosystem(BaseModel):
    tools_they_integrate_with: List[str] = Field(default_factory=list)
    partner_ecosystem: List[str] = Field(default_factory=list)
    api_maturity: ApiMaturity = ApiMaturity.unknown


class TechSignals(BaseModel):
    uses_modern_data_stack: Optional[bool] = None
    uses_crm: List[str] = Field(default_factory=list)
    uses_support_platform: List[str] = Field(default_factory=list)
    uses_marketing_tools: List[str] = Field(default_factory=list)


class TechEnvironment(BaseModel):
    inferred_stack: InferredStack = Field(default_factory=InferredStack)
    integrations_and_ecosystem: IntegrationsAndEcosystem = Field(default_factory=IntegrationsAndEcosystem)
    signals: TechSignals = Field(default_factory=TechSignals)


class LeadershipPerson(BaseModel):
    name: str = ""
    title: str = ""
    linkedin: str = ""
    notes: str = ""


class RelevantDepartments(BaseModel):
    titles_to_target: List[str] = Field(default_factory=lambda: [
        "VP Operations",
        "Head of RevOps",
        "Director of IT",
        "VP Customer Support",
        "Head of Fleet",
        "Director of Security"
    ])
    likely_owner_team: str = ""
    champion_profile: str = ""


class OpenRole(BaseModel):
    title: str = ""
    department: str = ""
    location: str = ""
    signal_tags: List[str] = Field(default_factory=lambda: ["revops", "data", "automation", "security", "scale"])
    url: str = ""


class HiringSignals(BaseModel):
    careers_url: str = ""
    open_roles: List[OpenRole] = Field(default_factory=list)
    inferred_priorities: List[str] = Field(default_factory=list)


class OrganizationAndPeople(BaseModel):
    leadership: List[LeadershipPerson] = Field(default_factory=list)
    relevant_departments: RelevantDepartments = Field(default_factory=RelevantDepartments)
    hiring_signals: HiringSignals = Field(default_factory=HiringSignals)


class PositioningLanguage(BaseModel):
    exact_phrases: List[str] = Field(default_factory=list)
    keywords_used: List[str] = Field(default_factory=list)
    objections_implied: List[str] = Field(default_factory=list)


class PersonalizationHook(BaseModel):
    hook: str = ""
    evidence: str = ""
    source_url: str = ""
    relevance: HookRelevance = HookRelevance.pain


class ValueHypothesis(BaseModel):
    hypothesis: str = ""
    why_now: str = ""
    expected_impact: str = ""
    who_cares: List[str] = Field(default_factory=list)


# class MessagingAndOutreach(BaseModel):
#     positioning_language: PositioningLanguage = Field(default_factory=PositioningLanguage)
#     personalization_hooks: List[PersonalizationHook] = Field(default_factory=list)
#     value_hypotheses: List[ValueHypothesis] = Field(default_factory=list)
#     qualification_questions_to_ask: List[str] = Field(default_factory=lambda: [
#         "What is your current process for X?",
#         "How do you measure Y today?",
#         "What happens if Z doesn't improve in the next quarter?"
#     ])


class HighSignalPage(BaseModel):
    page_type: HighSignalPageType
    url: HttpUrl
    bm25_score: Optional[float] = None
    url_prior: Optional[float] = None
    content_quality: Optional[float] = None
    notes: str = ""


# class IgnoreRulesApplied(BaseModel):
#     ignored_locales: List[str] = Field(default_factory=list)
#     ignored_subdomains: List[str] = Field(default_factory=list)
#     ignored_paths: List[str] = Field(default_factory=list)


class WebSignals(BaseModel):
    high_signal_pages: List[HighSignalPage] = Field(default_factory=list)


class CompetitiveLandscape(BaseModel):
    competitors_mentioned: List[str] = Field(default_factory=list)
    alternatives_likely: List[str] = Field(default_factory=list)


class Disqualifier(BaseModel):
    reason: str = ""
    severity: Severity = Severity.low
    evidence: str = ""


class RiskAndDisqualifiers(BaseModel):
    deal_risks: List[str] = Field(default_factory=list)
    competitive_landscape: CompetitiveLandscape = Field(default_factory=CompetitiveLandscape)
    disqualifiers: List[Disqualifier] = Field(default_factory=list)


# class RecommendedOutreachTarget(BaseModel):
#     persona: str = ""
#     title_examples: List[str] = Field(default_factory=list)
#     message_angle: str = ""


# class RecommendedSequence(BaseModel):
#     primary_channel: str = "email|linkedin|phone"
#     cadence_days: List[int] = Field(default_factory=lambda: [0, 2, 5, 9])
#     assets_to_send: List[str] = Field(default_factory=list)


# class Confidence(BaseModel):
#     overall: float = 0.0
#     data_completeness: float = 0.0


# class NextSteps(BaseModel):
#     recommended_outreach_targets: List[RecommendedOutreachTarget] = Field(default_factory=list)
#     recommended_sequence: RecommendedSequence = Field(default_factory=RecommendedSequence)
#     open_questions: List[str] = Field(default_factory=list)
#     confidence: Confidence = Field(default_factory=Confidence)


class Sources(BaseModel):
    scraped_urls: List[str] = Field(default_factory=list)
    last_updated_utc: str = ""
    notes: str = ""


# -------------------------
# Root Model
# -------------------------

class CompanyPersona(BaseModel):
    model_config = ConfigDict(extra="forbid")  # strict schema by default

    company: Company
    icp_fit: IcpFit = Field(default_factory=IcpFit)
    products_and_offering: ProductsAndOffering = Field(default_factory=ProductsAndOffering)
    customer_profile: CustomerProfile = Field(default_factory=CustomerProfile)
    pain_points_and_use_cases: PainPointsAndUseCases = Field(default_factory=PainPointsAndUseCases)
    budget_and_buying: BudgetAndBuying = Field(default_factory=BudgetAndBuying)
    tech_environment: TechEnvironment = Field(default_factory=TechEnvironment)
    organization_and_people: OrganizationAndPeople = Field(default_factory=OrganizationAndPeople)
    web_signals: WebSignals = Field(default_factory=WebSignals)
    risk_and_disqualifiers: RiskAndDisqualifiers = Field(default_factory=RiskAndDisqualifiers)
    sources: Sources = Field(default_factory=Sources)
