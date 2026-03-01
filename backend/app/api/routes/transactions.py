from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.transactions import BudgetSummaryResponse, ExpenseLogRequest, ExpenseLogResponse
from app.services.transactions import get_budget_summary, log_expense

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/log", response_model=ExpenseLogResponse)
def log_transaction(
    payload: ExpenseLogRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> ExpenseLogResponse:
    user_id = x_user_id or "demo-user"
    try:
        return log_expense(db=db, user_id=user_id, message=payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/budget-summary", response_model=BudgetSummaryResponse)
def budget_summary(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> BudgetSummaryResponse:
    user_id = x_user_id or "demo-user"
    try:
        return get_budget_summary(db=db, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
