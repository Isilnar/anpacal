import hashlib
import hmac

from cryptography.fernet import Fernet
from flask import current_app


def _fernet():
    key = current_app.config["FERNET_KEY"]
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


def encrypt_field(value):
    """Encrypt value with Fernet. Returns None when value is None."""
    if value is None:
        return None
    return _fernet().encrypt(value.encode()).decode()


def decrypt_field(value):
    """Decrypt value with Fernet. Returns None when value is None.
    Falls back to raw value on DecryptionError (plain-text legacy data)."""
    if value is None:
        return None
    try:
        return _fernet().decrypt(value.encode()).decode()
    except Exception:
        return value  # plain-text fallback (safe)


def hash_field(value):
    """Return HMAC-SHA256 hex (64 chars). Returns None when value is None."""
    if value is None:
        return None
    key = current_app.config["FERNET_KEY"]
    if isinstance(key, str):
        key = key.encode()
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
