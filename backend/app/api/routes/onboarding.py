from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.ai.factory import get_provider
from app.core.config import get_settings
from app.db import get_db
from app.schemas.onboarding import OnboardingMessageRequest, OnboardingResponse, OnboardingStartRequest
from app.services.onboarding import handle_onboarding_message, start_onboarding_session

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/start", response_model=OnboardingResponse)
def start_onboarding(
    payload: OnboardingStartRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> OnboardingResponse:
    user_id = x_user_id or "demo-user"
    settings = get_settings()
    provider = get_provider(settings)
    return start_onboarding_session(db=db, user_id=user_id, provider=provider.name, reset_existing=payload.reset_existing)


@router.post("/message", response_model=OnboardingResponse)
def onboarding_message(
    payload: OnboardingMessageRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> OnboardingResponse:
    user_id = x_user_id or "demo-user"
    settings = get_settings()
    provider = get_provider(settings)
    try:
        return handle_onboarding_message(
            db=db,
            user_id=user_id,
            provider=provider.name,
            session_id=payload.session_id,
            message=payload.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
