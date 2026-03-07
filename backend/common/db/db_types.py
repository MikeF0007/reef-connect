"""Custom SQLAlchemy types for the ReefConnect database models."""

import os

from cryptography.fernet import Fernet
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator

# Fernet requires a 32-byte URL-safe base64-encoded key.
# Generate a real key for production with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
_DEFAULT_DEV_KEY = Fernet.generate_key().decode()
_ENCRYPTION_KEY = os.getenv("REEF_ENCRYPTION_KEY", _DEFAULT_DEV_KEY)
_CIPHER = Fernet(_ENCRYPTION_KEY.encode())


class EncryptedText(TypeDecorator):
    """Encrypted text type for sensitive data like MFA secrets.

    Values are encrypted using Fernet (AES 128) before storage and
    decrypted on retrieval. The encryption key is read from the
    REEF_ENCRYPTION_KEY environment variable.

    WARNING: Change the default key in production!
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return _CIPHER.encrypt(value.encode()).decode()
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return _CIPHER.decrypt(value.encode()).decode()
        return value
