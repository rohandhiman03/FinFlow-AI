from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.digest import DigestSettingsRequest, DigestSettingsResponse, WeeklyDigestResponse
from app.services.digest import generate_weekly_digest, get_digest_settings, update_digest_settings

router = APIRouter(prefix="/digest", tags=["digest"])


@router.get("/settings", response_model=DigestSettingsResponse)
def get_settings_route(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> DigestSettingsResponse:
    user_id = x_user_id or "demo-user"
    return get_digest_settings(db=db, user_id=user_id)


@router.put("/settings", response_model=DigestSettingsResponse)
def update_settings_route(
    payload: DigestSettingsRequest,
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(default=None),
) -> DigestSettingsResponse:
    user_id = x_user_id or "demo-user"
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
    x_user_id: str | None = Header(default=None),
) -> WeeklyDigestResponse:
    user_id = x_user_id or "demo-user"
    try:
        return generate_weekly_digest(db=db, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
