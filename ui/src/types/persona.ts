export type PersonaConent = {
    company_name: string;
    industry: string;
    hq_location: string;
    mission_statement: string;
    core_products: CompanyProduct[];
    target_markets: TargetMarkets;
    sales_triggers: SalesTriggers;
    impact_metrics: ImpactMetrics[];
    sales_intelligence: SalesIntelligence;
    buyer_roles?: BuyerRole[];
    outbound_hooks?: OutboundHook[];
    buyer_messaging?: BuyerMessaging[];
};

export type CompanyProduct = {
    name: string;
    description: string;
};

export type TargetMarkets = {
    industries: string[];
    ideal_customer_profile: string;
};

export type SalesTriggers = {
    recent_funding_or_news: string;
    strategic_priorities: string;
};

export type ImpactMetrics = {
    case_study: string;
    result: string;
};

export type SalesIntelligence = {
    green_flags: string[];
    red_flags: string[];
    compliance_standards: string[];
};

export type BuyerRole = {
    title: string;
    department: string;
    daily_pain_points: string[];
    success_metrics: string[];
    typical_objections: string[];
};

export type OutboundHook = {
    hook_type: string;
    specific_signal: string;
    why_now: string;
    source_or_evidence: string;
};

export type BuyerMessaging = {
    role_title: string;
    value_prop: string;
    pain_to_solution: string;
    expected_outcome: string;
    opening_hook: string;
};

// ---------------------------------------------------------------------------
// Seller Brief — cross-referenced outreach guidance
// ---------------------------------------------------------------------------

export type FitAssessment = {
    fit_level: "Strong" | "Moderate" | "Weak";
    rationale: string;
    strongest_connection: string;
};

export type LeadAngle = {
    entry_point: string;
    why_this_first: string;
};

export type Positioning = {
    frame: string;
    against_priorities: string;
    differentiator_to_lead_with: string;
};

export type ObjectionMapEntry = {
    red_flag: string;
    how_to_handle: string;
    reframe: string;
};

export type OutreachTemplates = {
    email_subject: string | null;
    email_opener: string | null;
    call_opener: string | null;
};

export type SellerBrief = {
    fit_assessment: FitAssessment;
    lead_angle: LeadAngle;
    positioning: Positioning;
    objection_map: ObjectionMapEntry[];
    outreach_templates: OutreachTemplates;
};
