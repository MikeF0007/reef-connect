"""JWT token utilities for authentication."""

import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from common.config import settings


def create_access_token(user_id: uuid.UUID) -> str:
    """Create a signed JWT access token encoding the given user ID.

    Args:
        user_id: The UUID of the user to encode in the token.

    Returns:
        A signed JWT token string.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> uuid.UUID:
    """Decode a JWT access token and return the encoded user ID.

    Args:
        token: The raw JWT token string to decode.

    Returns:
        The user UUID extracted from the token's ``sub`` claim.

    Raises:
        ValueError: If the token is invalid, expired, or missing the ``sub`` claim.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        sub: str | None = payload.get("sub")
        if sub is None:
            raise ValueError("Token missing subject claim")
        return uuid.UUID(sub)
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
