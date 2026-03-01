from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class OnboardingStartRequest(BaseModel):
    reset_existing: bool = Field(default=False)


class OnboardingMessageRequest(BaseModel):
    session_id: str
    message: str


class BudgetProposal(BaseModel):
    estimated_monthly_income: float
    monthly_fixed_total: float
    monthly_variable_total: float
    suggested_savings: float
    categories: list[dict[str, float | str]]


class OnboardingResponse(BaseModel):
    session_id: str
    status: str
    current_step: str
    provider: str
    messages: list[ChatMessage]
    budget_proposal: BudgetProposal | None = None
