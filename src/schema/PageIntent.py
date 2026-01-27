from enum import Enum


class PageIntent(str, Enum):
    PRODUCT = "platform"
    USE_CASE = "use-case"
    INDUSTRY = "industry"
    PRICING = "pricing"
    ENTERPRISE = "enterprise"
    INTEGRATIONS = "integrations_api"
    MISSION = "mission"
    SECURITY = "security_trust"
    CUSTOMERS = "customers"
    SALES = "sales-contact"
    DOCS = "docs"
    OTHER = "other"
    IGNORE = "ignore"
