"""Repository interface protocols.

Each module contains a single Protocol class defining the contract for a
repository implementation.

Exports:
    IUserRepository: Protocol for user, profile, settings, and privacy data access.
    IUserCertificationRepository: Protocol for user certification data access.
    IDiveLogRepository: Protocol for dive log data access.
    IMediaRepository: Protocol for media and species tag data access.
"""

from common.db.repositories.interfaces.i_certification_repository import (
    IUserCertificationRepository,
)
from common.db.repositories.interfaces.i_dive_log_repository import IDiveLogRepository
from common.db.repositories.interfaces.i_media_repository import IMediaRepository
from common.db.repositories.interfaces.i_user_repository import IUserRepository

__all__ = [
    "IUserRepository",
    "IUserCertificationRepository",
    "IDiveLogRepository",
    "IMediaRepository",
]
