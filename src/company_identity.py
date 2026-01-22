from pydantic import BaseModel


class CompanyIdentity(BaseModel):
    name: str
    value_proposition: str
    target_icp: list[str]
    tech_stack_hints: list[str]
