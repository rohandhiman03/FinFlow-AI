from pydantic import BaseModel


class ExpenseLogRequest(BaseModel):
    message: str


class LoggedTransaction(BaseModel):
    id: str
    amount: float
    merchant: str
    category_name: str
    transaction_date: str


class ExpenseLogResponse(BaseModel):
    confirmation: str
    parsed_input: dict[str, str | float]
    transaction: LoggedTransaction


class BudgetCategorySummary(BaseModel):
    category_id: str
    name: str
    category_type: str
    planned_amount: float
    spent_amount: float
    remaining_amount: float
    utilization_pct: float
    status: str


class BudgetSummaryResponse(BaseModel):
    budget_id: str
    month: str
    total_planned: float
    total_spent: float
    total_remaining: float
    days_left_in_cycle: int
    projected_end_of_month_position: float
    categories: list[BudgetCategorySummary]
