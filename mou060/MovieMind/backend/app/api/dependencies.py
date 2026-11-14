"""Shared FastAPI dependencies."""

from __future__ import annotations

import uuid
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedApiError
from app.core.security import decode_access_token
from app.db.models.user import User
from app.db.session import get_db
from app.repositories import users as user_repo

# Request-scoped DB session, injected via Annotated to satisfy linters.
DbSession = Annotated[Session, Depends(get_db)]

_bearer = HTTPBearer(auto_error=False)
Credentials = Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)]


def get_current_user(db: DbSession, credentials: Credentials) -> User:
    """Resolve the authenticated user strictly from the bearer token.

    Never trusts a client-supplied user ID — identity comes only from the
    validated JWT ``sub`` claim.
    """
    if credentials is None:
        raise UnauthorizedApiError("Not authenticated")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedApiError("Token expired") from None
    except jwt.InvalidTokenError:
        raise UnauthorizedApiError("Invalid token") from None

    if payload.get("type") != "access":
        raise UnauthorizedApiError("Invalid token type")

    raw_sub = payload.get("sub")
    if not raw_sub:
        raise UnauthorizedApiError("Invalid token")
    try:
        user_id = uuid.UUID(raw_sub)
    except (ValueError, TypeError):
        raise UnauthorizedApiError("Invalid token") from None

    user = user_repo.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise UnauthorizedApiError("User not found or inactive")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
