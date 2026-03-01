from pydantic import BaseModel


class ScoreDimension(BaseModel):
    name: str
    score: float
    value: float
    ideal_range: str
    explanation: str


class CategoryPerformanceItem(BaseModel):
    category_name: str
    planned_amount: float
    actual_amount: float
    delta: float
    comment: str


class FinancialReportResponse(BaseModel):
    report_id: str
    month: str
    overall_score: float
    grade: str
    narrative: str
    dimensions: list[ScoreDimension]
    category_performance: list[CategoryPerformanceItem]
    insights: list[str]
    recommendation: str
    created_at: str
