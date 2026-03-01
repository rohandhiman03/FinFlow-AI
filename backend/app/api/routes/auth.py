from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security.dependencies import get_request_user_id
from app.core.security.jwt import create_access_token, hash_password, verify_password
from app.db import get_db
from app.db.models import ApiAccount
from app.schemas.auth import AuthResponse, LoginRequest, MeResponse, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = db.execute(select(ApiAccount).where(ApiAccount.email == payload.email.lower())).scalars().first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Email already registered")

    account = ApiAccount(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(account)
    db.commit()
    db.refresh(account)

    token = create_access_token(account.id)
    return AuthResponse(access_token=token, user_id=account.id)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    account = db.execute(select(ApiAccount).where(ApiAccount.email == payload.email.lower())).scalars().first()
    if account is None or not verify_password(payload.password, account.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(account.id)
    return AuthResponse(access_token=token, user_id=account.id)


@router.get("/me", response_model=MeResponse)
def me(user_id: str = Depends(get_request_user_id), db: Session = Depends(get_db)) -> MeResponse:
    account = db.get(ApiAccount, user_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return MeResponse(user_id=account.id, email=account.email)
