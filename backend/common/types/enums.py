"""Module defining enums used across the backend."""

from enum import Enum


class UnitSystem(Enum):
    IMPERIAL = "imperial"
    METRIC = "metric"


class Visibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    UNLISTED = "unlisted"


class DivePeriod(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    NIGHT = "night"


class DiveStartType(Enum):
    BOAT = "boat"
    SHORE = "shore"


class DiveType(Enum):
    REEF = "reef"
    WALL = "wall"
    DRIFT = "drift"
    CAVE = "cave"
    DEEP = "deep"
    SHIPWRECK = "shipwreck"
    OTHER = "other"


class DivePurpose(Enum):
    RECREATIONAL = "recreational"
    TRAINING = "training"
    RESEARCH = "research"
    RESTORATION = "restoration"
    OTHER = "other"


class Weather(Enum):
    SUNNY = "sunny"
    PARTLY_CLOUDY = "partly cloudy"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    WINDY = "windy"
    FOGGY = "foggy"


class WaterType(Enum):
    SALT = "salt"
    FRESH = "fresh"
    BRACKISH = "brackish"


class BodyOfWater(Enum):
    OCEAN = "ocean"
    LAKE = "lake"
    RIVER = "river"
    QUARRY = "quarry"
    CENOTE = "cenote"


class Condition(Enum):
    NONE = "none"
    LIGHT = "light"
    MODERATE = "moderate"
    STRONG = "strong"


class ExperienceFeeling(Enum):
    AMAZING = "amazing"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"


class MediaStatus(Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class MediaType(Enum):
    IMAGE = "image"
    VIDEO = "video"


class MLTaggingStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class SpeciesTagSource(Enum):
    USER = "user"
    ML = "ml"
