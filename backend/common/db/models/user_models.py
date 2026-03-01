"""Module providing user-related SQLAlchemy models.

This module defines the User, UserProfile, UserSettings, PrivacySettings, and UserCertification
models for authentication and user management.
"""

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    String,
    Text,
    func,
    JSON,
    ForeignKey,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID

# Use JSON for SQLite compatibility (JSONB not supported)
JSON_TYPE = JSON

from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.types import UnitSystem, Visibility
from common.db.db_types import EncryptedText
from .base_model import Base


class User(Base):
    """User model for authentication and basic user data."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    email_verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )
    auth_providers: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    mfa_secret: Mapped[Optional[str]] = mapped_column(EncryptedText)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile", back_populates="user", uselist=False
    )
    settings: Mapped[Optional["UserSettings"]] = relationship(
        "UserSettings", back_populates="user", uselist=False
    )
    privacy_settings: Mapped[Optional["PrivacySettings"]] = relationship(
        "PrivacySettings", back_populates="user", uselist=False
    )
    certifications: Mapped[List["UserCertification"]] = relationship(
        "UserCertification", back_populates="user"
    )
    dive_logs: Mapped[List["DiveLog"]] = relationship("DiveLog", back_populates="user")
    media: Mapped[List["Media"]] = relationship("Media", back_populates="user")
    scubadex_entries: Mapped[List["ScubadexEntry"]] = relationship(
        "ScubadexEntry", back_populates="user"
    )


class UserProfile(Base):
    """Extended user profile information."""

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    bio: Mapped[Optional[str]] = mapped_column(Text)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    avatar_storage_key: Mapped[Optional[str]] = mapped_column(Text)

    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    website_url: Mapped[Optional[str]] = mapped_column(Text)

    birth_date: Mapped[Optional[date]] = mapped_column(Date)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")


class UserSettings(Base):
    """User preferences and settings."""

    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    preferred_units: Mapped[UnitSystem] = mapped_column(
        SQLEnum(UnitSystem), default=UnitSystem.IMPERIAL, nullable=False
    )
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="settings")


class PrivacySettings(Base):
    """User privacy visibility settings."""

    __tablename__ = "privacy_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    profile_visibility: Mapped[Visibility] = mapped_column(
        SQLEnum(Visibility), default=Visibility.PUBLIC, nullable=False
    )
    dive_logs_visibility: Mapped[Visibility] = mapped_column(
        SQLEnum(Visibility), default=Visibility.PUBLIC, nullable=False
    )
    media_visibility: Mapped[Visibility] = mapped_column(
        SQLEnum(Visibility), default=Visibility.PUBLIC, nullable=False
    )
    stats_visibility: Mapped[Visibility] = mapped_column(
        SQLEnum(Visibility), default=Visibility.PUBLIC, nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="privacy_settings")


class UserCertification(Base):
    """User diving certifications."""

    __tablename__ = "user_certifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    certification_name: Mapped[str] = mapped_column(Text, nullable=False)
    issuer: Mapped[str] = mapped_column(Text, nullable=False)
    issued_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    certification_number: Mapped[Optional[str]] = mapped_column(Text)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    verified: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="certifications")
