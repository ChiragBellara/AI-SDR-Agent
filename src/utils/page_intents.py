from schema.PageIntent import PageIntent

INTENT_PATTERNS = {
    PageIntent.SECURITY: [
        r"security", r"trust", r"compliance", r"soc2", r"hipaa", r"gdpr", r"iso", r"dpa", r"radar", r"identity", r"tax"
    ],
    PageIntent.MISSION: [r"mission", r"statement"],
    PageIntent.PRICING: [r"pricing", r"plans"],
    PageIntent.ENTERPRISE: [r"enterprise"],
    PageIntent.SALES: [r"contact/sales", r"contact"],
    PageIntent.INTEGRATIONS: [r"integrations", r"api", r"developers", r"sdk", r"docs", r"webhooks"],
    PageIntent.USE_CASE: [r"use-cases", r"usecase"],
    PageIntent.INDUSTRY: [r"industries"],
    PageIntent.PRODUCT: [
        r"payments", r"billing", r"connect", r"issuing", r"invoicing", r"terminal",
        r"payouts", r"capital", r"financial", r"data-pipeline", r"sigma"
    ],
    PageIntent.CUSTOMERS: [r"customers", r"case-studies", r"testimonials"],
}

NEGATIVE_PATTERNS = [
    r"dashboard", r"login", r"signup", r"marketplace", r"careers",
    r"jobs", r"blog", r"press", r"news", r"events", r"status"
]

EXTENSIONS = [
    r"pdf", r"jpg", r"png", r"zip", r"docx", r"xml"
]

INTENT_WEIGHTS = {
    PageIntent.SECURITY: 15,
    PageIntent.PRICING: 15,
    PageIntent.MISSION: 12,
    PageIntent.ENTERPRISE: 12,
    PageIntent.INTEGRATIONS: 12,
    PageIntent.USE_CASE: 10,
    PageIntent.INDUSTRY: 9,
    PageIntent.PRODUCT: 8,
    PageIntent.CUSTOMERS: 7,
    PageIntent.SALES: 6,
    PageIntent.DOCS: 5,
}

INTENT_QUOTAS = {
    PageIntent.PRICING: 1,
    PageIntent.MISSION: 1,
    PageIntent.ENTERPRISE: 1,
    PageIntent.INTEGRATIONS: 2,
    PageIntent.USE_CASE: 2,
    PageIntent.INDUSTRY: 2,
    PageIntent.PRODUCT: 2,
    PageIntent.CUSTOMERS: 1,
}
