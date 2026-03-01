from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings
from app.core.security.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_request_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    x_user_id: str | None = Header(default=None),
) -> str:
    settings = get_settings()

    if settings.auth_enabled:
        if credentials is None:
            raise HTTPException(status_code=401, detail="Missing bearer token")
        try:
            return decode_access_token(credentials.credentials)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc

    # Dev mode fallback
    return x_user_id or "demo-user"
