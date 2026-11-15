"""Authentication endpoints (register, login, refresh, logout)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import DbSession, rate_limit_login, rate_limit_register
from app.core.config import get_settings
from app.core.errors import ConflictApiError, NotImplementedApiError, UnauthorizedApiError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories import users as user_repo
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse
from app.schemas.user import UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_token(user_id) -> TokenResponse:
    settings = get_settings()
    return TokenResponse(
        access_token=create_access_token(user_id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    dependencies=[Depends(rate_limit_register)],
    summary="Create account",
)
def register(payload: RegisterRequest, db: DbSession) -> RegisterResponse:
    email = payload.email.lower().strip()

    if user_repo.get_by_email(db, email) is not None:
        raise ConflictApiError("Email already registered")
    if payload.username and user_repo.get_by_username(db, payload.username) is not None:
        raise ConflictApiError("Username already taken")

    user = user_repo.create(
        db,
        email=email,
        password_hash=hash_password(payload.password),
        username=payload.username,
        display_name=payload.display_name,
    )

    token = _issue_token(user.id)
    return RegisterResponse(**token.model_dump(), user=UserOut.model_validate(user))


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_login)],
    summary="Authenticate and issue token",
)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    email = payload.email.lower().strip()
    user = user_repo.get_by_email(db, email)

    # Same generic message whether the email is unknown or the password is
    # wrong, to avoid account-enumeration leaks.
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.password_hash)
    ):
        raise UnauthorizedApiError("Invalid email or password")

    return _issue_token(user.id)


@router.post("/refresh", status_code=501, summary="Rotate tokens (unsupported)")
def refresh() -> None:
    raise NotImplementedApiError(
        "Refresh tokens are not supported in this release (access-token-only auth)"
    )


@router.post("/logout", status_code=501, summary="Revoke session (unsupported)")
def logout() -> None:
    raise NotImplementedApiError(
        "Server-side logout is not supported in this release; discard the token client-side"
    )
