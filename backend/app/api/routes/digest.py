from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security.dependencies import get_request_user_id
from app.db import get_db
from app.schemas.digest import DigestSettingsRequest, DigestSettingsResponse, WeeklyDigestResponse
from app.services.digest import generate_weekly_digest, get_digest_settings, update_digest_settings

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/settings", response_model=DigestSettingsResponse)
def get_settings_route(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_request_user_id),
) -> DigestSettingsResponse:
    return get_digest_settings(db=db, user_id=user_id)


@router.put("/settings", response_model=DigestSettingsResponse)
def update_settings_route(
    payload: DigestSettingsRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_request_user_id),
) -> DigestSettingsResponse:
    return update_digest_settings(
        db=db,
        user_id=user_id,
        frequency=payload.frequency,
        day=payload.day,
        time=payload.time,
    )


@router.get("/weekly", response_model=WeeklyDigestResponse)
def weekly_digest_route(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_request_user_id),
) -> WeeklyDigestResponse:
    try:
        return generate_weekly_digest(db=db, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
