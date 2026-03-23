"""Integration tests for authentication API endpoints."""

import bcrypt
import pytest

from api_service.app.core.security import create_access_token
from common.db.models.user_models import User


def _bcrypt_hash(plain: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


class TestAuthAPI:
    """Integration tests for /api/auth endpoints."""

    _EMAIL = "reef@example.com"
    _USERNAME = "reefuser"
    _PASSWORD = "password123"

    @pytest.fixture
    async def existing_user(self, async_session):
        """Insert a User with a known bcrypt password into the test database."""
        user = User(
            email=self._EMAIL,
            username=self._USERNAME,
            password_hash=_bcrypt_hash(self._PASSWORD),
        )
        async_session.add(user)
        await async_session.commit()
        await async_session.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self, existing_user):
        """Return Bearer Authorization headers for the pre-existing test user."""
        token = create_access_token(existing_user.id)
        return {"Authorization": f"Bearer {token}"}

    # ============================================================================
    # POST /api/auth/register
    # ============================================================================

    async def test_register_success(self, client):
        """Test successful registration returns 201 with user data and access token."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "username": "newuser",
                "password": self._PASSWORD,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["username"] == "newuser"
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client, existing_user):
        """Test registration with a duplicate email returns 409."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": self._EMAIL,
                "username": "differentuser",
                "password": self._PASSWORD,
            },
        )

        assert response.status_code == 409

    async def test_register_duplicate_username(self, client, existing_user):
        """Test registration with a duplicate username returns 409."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "different@example.com",
                "username": self._USERNAME,
                "password": self._PASSWORD,
            },
        )

        assert response.status_code == 409

    async def test_register_password_too_short(self, client):
        """Test registration with a password shorter than 8 characters returns 422."""
        response = client.post(
            "/api/auth/register",
            json={"email": "short@example.com", "username": "shortpass", "password": "pass"},
        )

        assert response.status_code == 422

    async def test_register_username_too_short(self, client):
        """Test registration with a username shorter than 3 characters returns 422."""
        response = client.post(
            "/api/auth/register",
            json={"email": "u@example.com", "username": "ab", "password": self._PASSWORD},
        )

        assert response.status_code == 422

    # ============================================================================
    # POST /api/auth/login
    # ============================================================================

    async def test_login_success(self, client, existing_user):
        """Test successful login returns 200 with user data and access token."""
        response = client.post(
            "/api/auth/login",
            json={"email": self._EMAIL, "password": self._PASSWORD},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["user"]["email"] == self._EMAIL
        assert data["user"]["username"] == self._USERNAME
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, existing_user):
        """Test login with wrong password returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"email": self._EMAIL, "password": "wrongpassword"},
        )

        assert response.status_code == 401

    async def test_login_unknown_email(self, client):
        """Test login with an unregistered email returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"email": "unknown@example.com", "password": self._PASSWORD},
        )

        assert response.status_code == 401

    # ============================================================================
    # POST /api/auth/logout
    # ============================================================================

    async def test_logout_success(self, client, auth_headers):
        """Test logout with a valid token returns 200 and success flag."""
        response = client.post("/api/auth/logout", headers=auth_headers)

        assert response.status_code == 200
        assert response.json() == {"success": True}

    async def test_logout_invalid_token(self, client):
        """Test logout with a malformed token returns 401."""
        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer not.a.valid.token"},
        )

        assert response.status_code == 401

    async def test_logout_no_token(self, client):
        """Test logout without an Authorization header returns 403."""
        response = client.post("/api/auth/logout")

        assert response.status_code == 403

    # ============================================================================
    # GET /api/auth/me
    # ============================================================================

    async def test_get_me_success(self, client, existing_user, auth_headers):
        """Test GET /api/auth/me returns the authenticated user's data."""
        response = client.get("/api/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == self._EMAIL
        assert data["username"] == self._USERNAME
        assert data["id"] == str(existing_user.id)

    async def test_get_me_invalid_token(self, client):
        """Test GET /api/auth/me with a malformed token returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401

    async def test_get_me_no_token(self, client):
        """Test GET /api/auth/me without an Authorization header returns 403."""
        response = client.get("/api/auth/me")

        assert response.status_code == 403
