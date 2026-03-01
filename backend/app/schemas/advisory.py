from pydantic import BaseModel


class AdvisoryAskRequest(BaseModel):
    message: str
    session_id: str | None = None


class AdvisorySuggestionItem(BaseModel):
    suggestion_id: str
    title: str
    summary: str
    adjustments: list[dict[str, float | str]]


class AdvisoryAskResponse(BaseModel):
    session_id: str
    answer: str
    reasoning: list[str]
    suggestions: list[AdvisorySuggestionItem]


class AdvisoryApplyRequest(BaseModel):
    suggestion_id: str


class AdvisoryApplyResponse(BaseModel):
    suggestion_id: str
    status: str
    applied_adjustments: list[dict[str, float | str]]
    confirmation: str
