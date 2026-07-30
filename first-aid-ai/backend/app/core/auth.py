from typing import Optional, Dict
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
import jwt

from .config import settings
from .bigquery_service import get_bq_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
# Bearer scheme for optional token extraction (does not auto-error when missing)
bearer_scheme = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except Exception:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    payload = _decode_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    bq = get_bq_service()
    user = bq.get_user_profile_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


async def get_optional_current_user(token: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> Optional[Dict]:
    """Return the authenticated user when token present and valid, otherwise return None.

    This is useful for endpoints that support both legacy unauthenticated requests (user_id in payload)
    and authenticated requests using JWTs.
    """
    if not token:
        return None
    token_str = getattr(token, "credentials", None)
    if not token_str:
        return None
    payload = _decode_token(token_str)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    bq = get_bq_service()
    user = bq.get_user_profile_by_id(user_id)
    return user



