"""FastAPI router for authentication endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from common.db.database import get_db_session
from common.db.repositories.user_repository import UserRepository

from ..core.security import create_access_token, decode_access_token
from ..schemas.user_schemas import AuthResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from ..services.auth_service import AuthService

_bearer = HTTPBearer()

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    """Dependency to create an AuthService instance.

    Args:
        session: AsyncSession for database operations.

    Returns:
        AuthService: An instance of AuthService.
    """
    return AuthService(UserRepository(session))


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UUID:
    """FastAPI dependency that validates a Bearer JWT and returns the user's UUID.

    Args:
        credentials: The HTTP Authorization header credentials.

    Returns:
        The UUID of the authenticated user.

    Raises:
        HTTPException(401): If the token is missing, invalid, or expired.
    """
    try:
        return decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    data: UserRegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Register a new user account.

    Args:
        data: Registration request containing email, username, and password.
        service: Auth service instance.

    Returns:
        AuthResponse: The new user's data and a signed JWT access token.
    """
    try:
        user_id = await service.register_user(
            email=data.email,
            username=data.username,
            password=data.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    user = await service.get_user_by_id(user_id)
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=create_access_token(user_id),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Authenticate a user and return a JWT access token.

    Args:
        data: Login request containing email and password.
        service: Auth service instance.

    Returns:
        AuthResponse: The user's data and a signed JWT access token.
    """
    user_id = await service.authenticate_user(email=data.email, password=data.password)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await service.get_user_by_id(user_id)
    return AuthResponse(
        user=UserResponse.model_validate(user),
        access_token=create_access_token(user_id),
    )


@router.post("/logout")
async def logout(
    _current_user_id: UUID = Depends(get_current_user_id),
) -> dict[str, bool]:
    """Signal the client to discard the current token.

    Tokens are stateless JWTs; server-side revocation is deferred to Phase 5.
    This endpoint validates the token so the client knows it was still valid at logout.

    Args:
        _current_user_id: The authenticated user's UUID (validated via JWT).

    Returns:
        dict: ``{"success": True}``
    """
    return {"success": True}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user_id: UUID = Depends(get_current_user_id),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Return the currently authenticated user's data.

    Args:
        current_user_id: The authenticated user's UUID (from JWT).
        service: Auth service instance.

    Returns:
        UserResponse: The authenticated user's data.
    """
    user = await service.get_user_by_id(current_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user not found",
        )
    return UserResponse.model_validate(user)
