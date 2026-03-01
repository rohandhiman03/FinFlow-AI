from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.reports import FinancialReportResponse
from app.services.reports import generate_financial_report, get_latest_financial_report, list_financial_reports

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/generate", response_model=FinancialReportResponse)
def generate_report(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> FinancialReportResponse:
    user_id = x_user_id or "demo-user"
    try:
        return generate_financial_report(db=db, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/latest", response_model=FinancialReportResponse)
def latest_report(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> FinancialReportResponse:
    user_id = x_user_id or "demo-user"
    try:
        return get_latest_financial_report(db=db, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/history", response_model=list[FinancialReportResponse])
def report_history(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> list[FinancialReportResponse]:
    user_id = x_user_id or "demo-user"
    return list_financial_reports(db=db, user_id=user_id)
