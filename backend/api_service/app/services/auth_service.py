"""Authentication service for user registration and login."""

import uuid

import bcrypt
from sqlalchemy.exc import IntegrityError

from common.db.models.user_models import User
from common.db.repositories.user_repository import UserRepository


class AuthService:
    """Provides user registration, login, and retrieval operations.

    Attributes:
        user_repository: The user repository for database operations.
    """

    def __init__(self, repository: UserRepository) -> None:
        self.user_repository = repository

    def _hash_password(self, plain: str) -> str:
        """Hash a plain-text password with bcrypt.

        Args:
            plain: The plain-text password to hash.

        Returns:
            The bcrypt-hashed password string.
        """
        return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, plain: str, hashed: str) -> bool:
        """Verify a plain-text password against a bcrypt hash.

        Args:
            plain: The plain-text password to check.
            hashed: The stored bcrypt hash to compare against.

        Returns:
            True if the password matches, False otherwise.
        """
        return bcrypt.checkpw(plain.encode(), hashed.encode())

    async def register_user(self, *, email: str, username: str, password: str) -> uuid.UUID:
        """Register a new user with a hashed password.

        Args:
            email: The user's email address.
            username: The user's chosen username.
            password: The plain-text password to hash and store.

        Returns:
            The UUID of the newly created user.

        Raises:
            ValueError: If the email or username is already registered.
        """
        try:
            return await self.user_repository.create_user(
                email=email,
                username=username,
                password_hash=self._hash_password(password),
            )
        except IntegrityError as exc:
            raise ValueError("Email or username already registered") from exc

    async def authenticate_user(self, *, email: str, password: str) -> uuid.UUID | None:
        """Verify credentials and return the user ID on success.

        Args:
            email: The user's email address.
            password: The plain-text password to verify.

        Returns:
            The user's UUID if credentials are valid, otherwise ``None``.
        """
        user = await self.user_repository.get_user_by_email(email)
        if user is None or not self._verify_password(password, user.password_hash):
            return None
        return user.id

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user by their UUID.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The User instance if found, otherwise ``None``.
        """
        return await self.user_repository.get_user_by_id(user_id)
