"""Module providing core data SQLAlchemy models.

This module defines the main business models for dive logging, media management, and species
tracking.
"""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Date,
    DECIMAL,
    DateTime,
    Integer,
    String,
    Text,
    func,
    JSON,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID

# Use JSON for SQLite compatibility (JSONB not supported in SQLite)
JSON_TYPE = JSON

from common.types import (
    DivePeriod,
    DiveStartType,
    DiveType,
    DivePurpose,
    Weather,
    WaterType,
    BodyOfWater,
    Condition,
    ExperienceFeeling,
    Visibility,
    MediaStatus,
    MediaType,
    MLTaggingStatus,
    SpeciesTagSource,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import Base
from common.db.db_types import PointGeography


class DiveLog(Base):
    """Dive log entry model.

    Maps to the ``dive_logs`` table defined in er_core_data.puml.
    All measurement values are stored in imperial units (feet / °F / PSI).
    The ``location`` field uses ``PointGeography``, which renders as
    ``geography(Point,4326)`` on PostgreSQL and ``TEXT`` on SQLite.
    """

    __tablename__ = "dive_logs"

    # --- Required fields ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dive_date: Mapped[date] = mapped_column(Date, nullable=False)
    dive_title: Mapped[str] = mapped_column(Text, nullable=False)
    dive_site: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Dive Basics ---
    dive_period: Mapped[Optional[DivePeriod]] = mapped_column(SQLEnum(DivePeriod))
    dive_start_type: Mapped[Optional[DiveStartType]] = mapped_column(
        SQLEnum(DiveStartType)
    )
    dive_type: Mapped[Optional[DiveType]] = mapped_column(SQLEnum(DiveType))
    dive_purpose: Mapped[Optional[DivePurpose]] = mapped_column(SQLEnum(DivePurpose))

    # --- Measurements ---
    max_depth_ft: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(6, 2))
    avg_depth_ft: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(6, 2))
    visibility_ft: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(6, 2))
    visibility_description: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(PointGeography)

    # --- Environmental ---
    weather: Mapped[Optional[Weather]] = mapped_column(SQLEnum(Weather))
    air_temp_f: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    surface_temp_f: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    bottom_temp_f: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 2))
    water_type: Mapped[Optional[WaterType]] = mapped_column(SQLEnum(WaterType))
    body_of_water: Mapped[Optional[BodyOfWater]] = mapped_column(SQLEnum(BodyOfWater))
    wave: Mapped[Optional[Condition]] = mapped_column(SQLEnum(Condition))
    current: Mapped[Optional[Condition]] = mapped_column(SQLEnum(Condition))
    surge: Mapped[Optional[Condition]] = mapped_column(SQLEnum(Condition))

    # --- Equipment ---
    equipment: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    gas_mix: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    cylinder_pressure: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    safety_stops: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)

    # --- People / Experience ---
    buddy: Mapped[Optional[str]] = mapped_column(Text)
    dive_center: Mapped[Optional[str]] = mapped_column(Text)
    experience_feeling: Mapped[Optional[ExperienceFeeling]] = mapped_column(
        SQLEnum(ExperienceFeeling)
    )
    experience_rating: Mapped[Optional[int]] = mapped_column(
        Integer,
        CheckConstraint(
            "experience_rating >= 1 AND experience_rating <= 5",
            name="experience_rating_range",
        ),
    )  # 1–5
    public_notes: Mapped[Optional[str]] = mapped_column(Text)
    private_notes: Mapped[Optional[str]] = mapped_column(Text)

    # --- Visibility ---
    log_visibility: Mapped[Optional[Visibility]] = mapped_column(SQLEnum(Visibility))

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="dive_logs")
    media: Mapped[List["Media"]] = relationship("Media", back_populates="dive_log")


class Media(Base):
    """Media file model for photos and videos.

    Maps to the ``media`` table defined in er_core_data.puml.
    """

    __tablename__ = "media"

    # --- Required fields ---
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        SQLEnum(MediaStatus), nullable=False, default=MediaStatus.PENDING
    )
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(SQLEnum(MediaType), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Associations ---
    dive_log_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dive_logs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    ml_tagging_status: Mapped[Optional[MLTaggingStatus]] = mapped_column(
        SQLEnum(MLTaggingStatus)
    )

    # --- Media Details ---
    mime_type: Mapped[Optional[str]] = mapped_column(Text)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    duration_seconds: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 3))
    taken_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    exif: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    processed_versions: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # --- Visibility ---
    media_visibility: Mapped[Optional[Visibility]] = mapped_column(SQLEnum(Visibility))

    # --- Meta ---
    error_details: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="media")
    dive_log: Mapped[Optional["DiveLog"]] = relationship(
        "DiveLog", back_populates="media"
    )
    species_tags: Mapped[List["MediaSpeciesTag"]] = relationship(
        "MediaSpeciesTag", back_populates="media", cascade="all, delete-orphan"
    )


class Species(Base):
    """Marine species model.

    Maps to the ``species`` table defined in er_core_data.puml.
    Seeded from ML labels (data/ml_labels.json).
    """

    __tablename__ = "species"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ml_label: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    scientific_name: Mapped[str] = mapped_column(Text, nullable=False)
    common_name: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Species Details ---
    slug: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    habitat: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    locations: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    taxonomy: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)
    image_urls: Mapped[Optional[dict]] = mapped_column(JSON_TYPE)

    # Relationships
    media_tags: Mapped[List["MediaSpeciesTag"]] = relationship(
        "MediaSpeciesTag", back_populates="species"
    )
    scubadex_entries: Mapped[List["ScubadexEntry"]] = relationship(
        "ScubadexEntry", back_populates="species"
    )


class MediaSpeciesTag(Base):
    """Junction table linking media to species tags.

    Maps to the ``media_species_tags`` table defined in er_core_data.puml.
    Uses a composite primary key (media_id, species_id) — no surrogate id.
    """

    __tablename__ = "media_species_tags"

    media_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("media.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    species_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("species.id"),
        primary_key=True,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(SQLEnum(SpeciesTagSource), nullable=False)
    tagged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    model_confidence: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 4)
    )  # 0.0–1.0 for ML tags

    # Relationships
    media: Mapped["Media"] = relationship("Media", back_populates="species_tags")
    species: Mapped["Species"] = relationship("Species", back_populates="media_tags")


class ScubadexEntry(Base):
    """Denormalized user species collection.

    Maps to the ``scubadex_entries`` table defined in er_core_data.puml.
    Maintained event-driven by MaterializedDataWorker.
    """

    __tablename__ = "scubadex_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "species_id", name="uq_scubadex_user_species"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    species_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("species.id"), nullable=False, index=True
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
    times_encountered: Mapped[int] = mapped_column(Integer, nullable=False)
    date_first_encountered: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="scubadex_entries")
    species: Mapped["Species"] = relationship(
        "Species", back_populates="scubadex_entries"
    )
