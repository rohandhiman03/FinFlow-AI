from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security.dependencies import get_request_user_id
from app.db import get_db
from app.schemas.transactions import BudgetSummaryResponse, ExpenseLogRequest, ExpenseLogResponse
from app.services.transactions import get_budget_summary, log_expense

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/log", response_model=ExpenseLogResponse)
def log_transaction(
    payload: ExpenseLogRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_request_user_id),
) -> ExpenseLogResponse:
    try:
        return log_expense(db=db, user_id=user_id, message=payload.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/budget-summary", response_model=BudgetSummaryResponse)
def budget_summary(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_request_user_id),
) -> BudgetSummaryResponse:
    try:
        return get_budget_summary(db=db, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
