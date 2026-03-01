from pydantic import BaseModel


class GoalCreateRequest(BaseModel):
    name: str
    target_amount: float
    target_date: str | None = None


class GoalContributeRequest(BaseModel):
    amount: float


class GoalItem(BaseModel):
    goal_id: str
    name: str
    target_amount: float
    current_amount: float
    progress_pct: float
    target_date: str
    required_monthly: float
    on_track: bool


class GoalContributeResponse(BaseModel):
    goal_id: str
    current_amount: float
    progress_pct: float
    confirmation: str
