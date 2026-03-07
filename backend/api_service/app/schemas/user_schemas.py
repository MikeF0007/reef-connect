"""Pydantic schemas for user-related API endpoints."""

from datetime import date as Date, datetime as DateTime
from typing import Optional
from uuid import UUID

from common.types.enums import UnitSystem, Visibility
from pydantic import BaseModel, Field


class UserProfileCreate(BaseModel):
    """Schema for creating a user profile."""

    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = None
    website_url: Optional[str] = None
    birth_date: Optional[Date] = None


class UserProfileUpdate(BaseModel):
    """Schema for updating a user profile."""

    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = None
    website_url: Optional[str] = None
    birth_date: Optional[Date] = None


class UserProfileResponse(BaseModel):
    """Schema for user profile response."""

    id: UUID
    user_id: UUID
    created_at: DateTime
    updated_at: DateTime
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    location: Optional[str] = None
    website_url: Optional[str] = None
    birth_date: Optional[Date] = None

    model_config = {"from_attributes": True}


class UserSettingsCreate(BaseModel):
    """Schema for creating user settings."""

    preferred_units: UnitSystem = UnitSystem.IMPERIAL
    timezone: str = "UTC"
    language: str = "en"
    notifications_enabled: bool = True


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings."""

    preferred_units: Optional[UnitSystem] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    """Schema for user settings response."""

    id: UUID
    user_id: UUID
    created_at: DateTime
    updated_at: DateTime
    preferred_units: UnitSystem
    timezone: str
    language: str
    notifications_enabled: bool

    model_config = {"from_attributes": True}


class PrivacySettingsCreate(BaseModel):
    """Schema for creating privacy settings."""

    profile_visibility: Visibility = Visibility.PUBLIC
    dive_logs_visibility: Visibility = Visibility.PUBLIC
    media_visibility: Visibility = Visibility.PUBLIC
    stats_visibility: Visibility = Visibility.PUBLIC


class PrivacySettingsUpdate(BaseModel):
    """Schema for updating privacy settings."""

    profile_visibility: Optional[Visibility] = None
    dive_logs_visibility: Optional[Visibility] = None
    media_visibility: Optional[Visibility] = None
    stats_visibility: Optional[Visibility] = None


class PrivacySettingsResponse(BaseModel):
    """Schema for privacy settings response."""

    id: UUID
    user_id: UUID
    created_at: DateTime
    updated_at: DateTime
    profile_visibility: Visibility
    dive_logs_visibility: Visibility
    media_visibility: Visibility
    stats_visibility: Visibility

    model_config = {"from_attributes": True}


class UserCertificationCreate(BaseModel):
    """Schema for creating a user certification."""

    certification_name: str = Field(min_length=1)
    issuer: str = Field(min_length=1)
    issued_date: Date
    expiry_date: Optional[Date] = None
    certification_number: Optional[str] = None
    notes: Optional[str] = None
    verified: Optional[bool] = None


class UserCertificationUpdate(BaseModel):
    """Schema for updating a user certification."""

    certification_name: Optional[str] = None
    issuer: Optional[str] = None
    issued_date: Optional[Date] = None
    expiry_date: Optional[Date] = None
    certification_number: Optional[str] = None
    notes: Optional[str] = None
    verified: Optional[bool] = None


class UserCertificationResponse(BaseModel):
    """Schema for user certification response."""

    id: UUID
    user_id: UUID
    created_at: DateTime
    updated_at: DateTime
    certification_name: str
    issuer: str
    issued_date: Date
    expiry_date: Optional[Date] = None
    certification_number: Optional[str] = None
    notes: Optional[str] = None
    verified: Optional[bool] = None

    model_config = {"from_attributes": True}
