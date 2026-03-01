"""Database repository layer.

Exports:
    IUserRepository: Protocol for user-related data access operations.
    UserRepository: Implementation of IUserRepository.
    IUserCertificationRepository: Protocol for certification data access operations.
    UserCertificationRepository: Implementation of IUserCertificationRepository.
    IDiveLogRepository: Protocol for dive log data access operations.
    DiveLogRepository: Implementation of IDiveLogRepository.
"""

from common.db.repositories.interfaces import (
    IDiveLogRepository,
    IUserCertificationRepository,
    IUserRepository,
)
from common.db.repositories.user_certification_repository import (
    UserCertificationRepository,
)
from common.db.repositories.user_repository import UserRepository
from common.db.repositories.dive_log_repository import DiveLogRepository

__all__ = [
    "IUserRepository",
    "UserRepository",
    "IUserCertificationRepository",
    "UserCertificationRepository",
    "IDiveLogRepository",
    "DiveLogRepository",
]
