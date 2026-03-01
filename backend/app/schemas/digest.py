from pydantic import BaseModel


class DigestSettingsRequest(BaseModel):
    frequency: str
    day: str
    time: str


class DigestSettingsResponse(BaseModel):
    frequency: str
    day: str
    time: str


class WeeklyDigestResponse(BaseModel):
    period_start: str
    period_end: str
    weekly_spent: float
    weekly_income_proxy: float
    savings_rate_pct: float
    category_to_watch: str
    upcoming_expenses: list[dict[str, str | float]]
    digest_text: str
