from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.statements import (
    ConfirmGapRequest,
    ConfirmGapResponse,
    ReconciliationResponse,
    StatementListItem,
    StatementUploadResponse,
)
from app.services.statements import confirm_gap, get_reconciliation, list_statements, upload_statement

router = APIRouter(prefix="/statements", tags=["statements"])


@router.post("/upload", response_model=StatementUploadResponse)
async def upload_statement_route(
    file: UploadFile = File(...),
    account_name: str = Form(default="Primary Account"),
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> StatementUploadResponse:
    user_id = x_user_id or "demo-user"
    content = await file.read()
    try:
        return upload_statement(
            db=db,
            user_id=user_id,
            account_name=account_name,
            filename=file.filename or "statement.csv",
            content=content,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[StatementListItem])
def list_statements_route(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> list[StatementListItem]:
    user_id = x_user_id or "demo-user"
    return list_statements(db=db, user_id=user_id)


@router.get("/{statement_id}/reconciliation", response_model=ReconciliationResponse)
def get_reconciliation_route(
    statement_id: str,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> ReconciliationResponse:
    user_id = x_user_id or "demo-user"
    try:
        return get_reconciliation(db=db, user_id=user_id, statement_id=statement_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{statement_id}/gaps/{entry_id}/confirm", response_model=ConfirmGapResponse)
def confirm_gap_route(
    statement_id: str,
    entry_id: str,
    payload: ConfirmGapRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> ConfirmGapResponse:
    user_id = x_user_id or "demo-user"
    try:
        return confirm_gap(
            db=db,
            user_id=user_id,
            statement_id=statement_id,
            entry_id=entry_id,
            category_name=payload.category_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
