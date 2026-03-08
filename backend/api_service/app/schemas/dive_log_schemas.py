"""Pydantic schemas for dive log API endpoints.

Unit Conversion Architecture:
- Database stores all measurements in imperial units (feet, °F, PSI) as canonical format
- API fields are unit-agnostic and accept/return data in user's preferred units (metric/imperial)
- Aliases map API field names to database column names
- Unit conversion is handled in the service layer based on user preferences
- Affected fields: distances (max_depth, avg_depth, visibility), temperatures (air_temp, surface_temp, bottom_temp)
- JSON fields (equipment, gas_mix, cylinder_pressure, safety_stops) may contain measurements but require complex parsing
"""

from datetime import date as Date, datetime as DateTime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from common.types.enums import (
    BodyOfWater,
    Condition,
    DivePeriod,
    DivePurpose,
    DiveStartType,
    DiveType,
    ExperienceFeeling,
    Visibility,
    WaterType,
    Weather,
)
from pydantic import BaseModel, Field


class DiveLogCreate(BaseModel):
    """Schema for creating a dive log entry."""

    date: Date = Field(..., alias="dive_date")
    title: str = Field(..., min_length=1, max_length=255, alias="dive_title")
    site: str = Field(..., min_length=1, max_length=255, alias="dive_site")
    duration: int = Field(..., gt=0, alias="duration_minutes")

    # Optional dive basics
    period: Optional[DivePeriod] = Field(None, alias="dive_period")
    start_type: Optional[DiveStartType] = Field(None, alias="dive_start_type")
    type: Optional[DiveType] = Field(None, alias="dive_type")
    purpose: Optional[DivePurpose] = Field(None, alias="dive_purpose")

    # Required measurements
    max_depth: Decimal = Field(
        ..., max_digits=6, decimal_places=2, alias="max_depth_ft"
    )
    avg_depth: Optional[Decimal] = Field(
        None, max_digits=6, decimal_places=2, alias="avg_depth_ft"
    )
    visibility: Optional[Decimal] = Field(
        None, max_digits=6, decimal_places=2, alias="visibility_ft"
    )
    visibility_description: Optional[str] = None
    lat: Optional[Decimal] = Field(None, ge=-90, le=90, max_digits=9, decimal_places=6)
    long: Optional[Decimal] = Field(
        None, ge=-180, le=180, max_digits=9, decimal_places=6
    )

    # Required visibility
    log_visibility: Visibility = Field(...)

    # Optional environmental
    weather: Optional[Weather] = None
    air_temp: Optional[Decimal] = Field(
        None, max_digits=5, decimal_places=2, alias="air_temp_f"
    )
    surface_temp: Optional[Decimal] = Field(
        None, max_digits=5, decimal_places=2, alias="surface_temp_f"
    )
    bottom_temp: Optional[Decimal] = Field(
        None, max_digits=5, decimal_places=2, alias="bottom_temp_f"
    )
    water_type: Optional[WaterType] = None
    body_of_water: Optional[BodyOfWater] = None
    wave: Optional[Condition] = None
    current: Optional[Condition] = None
    surge: Optional[Condition] = None

    # Optional equipment
    equipment: Optional[dict] = None
    gas_mix: Optional[dict] = None
    cylinder_pressure: Optional[dict] = None
    safety_stops: Optional[dict] = None

    # Optional people/experience
    buddy: Optional[str] = None
    dive_center: Optional[str] = None
    experience_feeling: Optional[ExperienceFeeling] = None
    experience_rating: Optional[int] = Field(None, ge=1, le=5)
    public_notes: Optional[str] = None
    private_notes: Optional[str] = None

    model_config = {"populate_by_name": True}


class DiveLogUpdate(BaseModel):
    """Schema for updating a dive log entry."""

    date: Optional[Date] = Field(None, alias="dive_date")
    title: Optional[str] = Field(None, min_length=1, max_length=255, alias="dive_title")
    site: Optional[str] = Field(None, min_length=1, max_length=255, alias="dive_site")
    duration: Optional[int] = Field(None, gt=0, alias="duration_minutes")

    # Optional dive basics
    period: Optional[DivePeriod] = Field(None, alias="dive_period")
    start_type: Optional[DiveStartType] = Field(None, alias="dive_start_type")
    type: Optional[DiveType] = Field(None, alias="dive_type")
    purpose: Optional[DivePurpose] = Field(None, alias="dive_purpose")

    # Optional measurements
    max_depth: Optional[Decimal] = Field(
        None, max_digits=6, decimal_places=2, alias="max_depth_ft"
    )
    avg_depth: Optional[Decimal] = Field(
        None, max_digits=6, decimal_places=2, alias="avg_depth_ft"
    )
    visibility: Optional[Decimal] = Field(
        None, max_digits=6, decimal_places=2, alias="visibility_ft"
    )
    visibility_description: Optional[str] = None
    lat: Optional[Decimal] = Field(None, ge=-90, le=90, max_digits=9, decimal_places=6)
    long: Optional[Decimal] = Field(
        None, ge=-180, le=180, max_digits=9, decimal_places=6
    )

    # Optional visibility
    log_visibility: Optional[Visibility] = Field(None)

    # Optional environmental
    weather: Optional[Weather] = None
    air_temp: Optional[Decimal] = Field(
        None, max_digits=5, decimal_places=2, alias="air_temp_f"
    )
    surface_temp: Optional[Decimal] = Field(
        None, max_digits=5, decimal_places=2, alias="surface_temp_f"
    )
    bottom_temp: Optional[Decimal] = Field(
        None, max_digits=5, decimal_places=2, alias="bottom_temp_f"
    )
    water_type: Optional[WaterType] = None
    body_of_water: Optional[BodyOfWater] = None
    wave: Optional[Condition] = None
    current: Optional[Condition] = None
    surge: Optional[Condition] = None

    # Optional equipment
    equipment: Optional[dict] = None
    gas_mix: Optional[dict] = None
    cylinder_pressure: Optional[dict] = None
    safety_stops: Optional[dict] = None

    # Optional people/experience
    buddy: Optional[str] = None
    dive_center: Optional[str] = None
    experience_feeling: Optional[ExperienceFeeling] = None
    experience_rating: Optional[int] = Field(None, ge=1, le=5)
    public_notes: Optional[str] = None
    private_notes: Optional[str] = None

    # Optional visibility
    visibility: Optional[Visibility] = Field(None, alias="log_visibility")

    model_config = {"populate_by_name": True}


class DiveLogResponse(BaseModel):
    """Schema for dive log response."""

    id: UUID
    user_id: UUID
    created_at: DateTime
    updated_at: DateTime

    date: Date = Field(..., alias="dive_date")
    title: str = Field(..., alias="dive_title")
    site: str = Field(..., alias="dive_site")
    duration: int = Field(..., alias="duration_minutes")

    # Optional dive basics
    period: Optional[DivePeriod] = Field(None, alias="dive_period")
    start_type: Optional[DiveStartType] = Field(None, alias="dive_start_type")
    type: Optional[DiveType] = Field(None, alias="dive_type")
    purpose: Optional[DivePurpose] = Field(None, alias="dive_purpose")

    # Optional measurements
    max_depth: Optional[Decimal] = Field(None, alias="max_depth_ft")
    avg_depth: Optional[Decimal] = Field(None, alias="avg_depth_ft")
    visibility: Optional[Decimal] = Field(None, alias="visibility_ft")
    visibility_description: Optional[str] = None
    lat: Optional[Decimal] = None
    long: Optional[Decimal] = None

    # Optional environmental
    weather: Optional[Weather] = None
    air_temp: Optional[Decimal] = Field(None, alias="air_temp_f")
    surface_temp: Optional[Decimal] = Field(None, alias="surface_temp_f")
    bottom_temp: Optional[Decimal] = Field(None, alias="bottom_temp_f")
    water_type: Optional[WaterType] = None
    body_of_water: Optional[BodyOfWater] = None
    wave: Optional[Condition] = None
    current: Optional[Condition] = None
    surge: Optional[Condition] = None

    # Optional equipment
    equipment: Optional[dict] = None
    gas_mix: Optional[dict] = None
    cylinder_pressure: Optional[dict] = None
    safety_stops: Optional[dict] = None

    # Optional people/experience
    buddy: Optional[str] = None
    dive_center: Optional[str] = None
    experience_feeling: Optional[ExperienceFeeling] = None
    experience_rating: Optional[int] = None
    public_notes: Optional[str] = None
    private_notes: Optional[str] = None

    # Optional visibility
    log_visibility: Optional[Visibility] = Field(None)

    model_config = {"from_attributes": True, "populate_by_name": True, "by_alias": True}


class DiveLogQuery(BaseModel):
    """Schema for dive log query parameters."""

    sort_by: Optional[str] = Field(
        "date", pattern="^(date|max_depth|duration|location|experience_rating)$"
    )
    order: Optional[str] = Field("desc", pattern="^(asc|desc)$")
    limit: Optional[int] = Field(None, gt=0, le=100)
    offset: Optional[int] = Field(0, ge=0)


class DiveLogDateRangeQuery(DiveLogQuery):
    """Schema for dive log date range queries."""

    start_date: Date
    end_date: Date
