from pydantic import BaseModel, Field
from typing import List, Optional


class LeadCard(BaseModel):
    company_name: str
    category: Optional[str] = None
    one_liner: str
    products_or_platform: List[str] = Field(default_factory=list)
    target_customers: List[str] = Field(default_factory=list)
    core_workflows: List[str] = Field(default_factory=list)
    technical_surface_area: List[str] = Field(default_factory=list)
    integrations_or_stack_hints: List[str] = Field(default_factory=list)
    compliance_or_regulatory_signals: List[str] = Field(default_factory=list)
    scale_and_growth_signals: List[str] = Field(default_factory=list)
    common_pain_points: List[str] = Field(default_factory=list)
    buyer_roles: List[str] = Field(default_factory=list)
    # relevance_score: int
    notable_keywords: List[str] = Field(default_factory=list)
    source_notes: List[str] = Field(default_factory=list)
