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
"""

from common.db.repositories.interfaces import (
    IDiveLogRepository,
    IMediaRepository,
    IUserCertificationRepository,
    IUserRepository,
)
from common.db.repositories.user_certification_repository import (
    UserCertificationRepository,
)
from common.db.repositories.user_repository import UserRepository
from common.db.repositories.dive_log_repository import DiveLogRepository
from common.db.repositories.media_repository import MediaRepository

__all__ = [
    "IUserRepository",
    "UserRepository",
    "IUserCertificationRepository",
    "UserCertificationRepository",
    "IDiveLogRepository",
    "DiveLogRepository",
    "IMediaRepository",
    "MediaRepository",
]
