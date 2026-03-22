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
    red_flags: string;
    compliance_standards: string[];
};
