from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.advisory import AdvisoryApplyRequest, AdvisoryApplyResponse, AdvisoryAskRequest, AdvisoryAskResponse
from app.services.advisory import apply_suggestion, ask_advisory_question

router = APIRouter(prefix="/advisory", tags=["advisory"])


@router.post("/ask", response_model=AdvisoryAskResponse)
def ask_advisory(
    payload: AdvisoryAskRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> AdvisoryAskResponse:
    user_id = x_user_id or "demo-user"
    try:
        return ask_advisory_question(
            db=db,
            user_id=user_id,
            session_id=payload.session_id,
            message=payload.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/apply", response_model=AdvisoryApplyResponse)
def apply_advisory(
    payload: AdvisoryApplyRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> AdvisoryApplyResponse:
    user_id = x_user_id or "demo-user"
    try:
        return apply_suggestion(db=db, user_id=user_id, suggestion_id=payload.suggestion_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
