"""Database repository layer.

Exports:
    IUserRepository: Protocol for user-related data access operations.
    UserRepository: Implementation of IUserRepository.
    IUserCertificationRepository: Protocol for certification data access operations.
    UserCertificationRepository: Implementation of IUserCertificationRepository.
    IDiveLogRepository: Protocol for dive log data access operations.
    DiveLogRepository: Implementation of IDiveLogRepository.
    IMediaRepository: Protocol for media data access operations.
    MediaRepository: Implementation of IMediaRepository.
    ISpeciesTagRepository: Protocol for species tag data access operations.
    SpeciesTagRepository: Implementation of ISpeciesTagRepository.
    ISpeciesRepository: Protocol for species catalog data access operations.
    SpeciesRepository: Implementation of ISpeciesRepository.
"""

from common.db.repositories.interfaces import (
    IDiveLogRepository,
    IMediaRepository,
    ISpeciesRepository,
    ISpeciesTagRepository,
    IUserCertificationRepository,
    IUserRepository,
)
from common.db.repositories.user_certification_repository import (
    UserCertificationRepository,
)
from common.db.repositories.user_repository import UserRepository
from common.db.repositories.dive_log_repository import DiveLogRepository
from common.db.repositories.media_repository import MediaRepository
from common.db.repositories.species_repository import SpeciesRepository
from common.db.repositories.species_tag_repository import SpeciesTagRepository

__all__ = [
    "IUserRepository",
    "UserRepository",
    "IUserCertificationRepository",
    "UserCertificationRepository",
    "IDiveLogRepository",
    "DiveLogRepository",
    "IMediaRepository",
    "MediaRepository",
    "ISpeciesTagRepository",
    "SpeciesTagRepository",
    "ISpeciesRepository",
    "SpeciesRepository",
]
