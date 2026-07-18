"""
Tests unitarios para app/infrastructure/crypto.py.

Bcrypt/Fernet siempre activo — usa el fixture `app` del conftest.
"""

import pytest

# ---------------------------------------------------------------------------
# encrypt_field
# ---------------------------------------------------------------------------


class TestEncryptField:
    def test_encrypt_returns_fernet_token(self, app):
        """Devuelve un token Fernet (string diferente al input)."""
        with app.app_context():
            from app.infrastructure.crypto import encrypt_field

            result = encrypt_field("secret_value")
            assert result is not None
            assert isinstance(result, str)
            assert result != "secret_value"

    def test_encrypt_none_returns_none(self, app):
        """valor None → devuelve None."""
        with app.app_context():
            from app.infrastructure.crypto import encrypt_field

            assert encrypt_field(None) is None


# ---------------------------------------------------------------------------
# decrypt_field
# ---------------------------------------------------------------------------


class TestDecryptField:
    def test_decrypt_round_trip(self, app):
        """Descifra correctamente lo que encrypt produjo."""
        with app.app_context():
            from app.infrastructure.crypto import decrypt_field, encrypt_field

            original = "round_trip_value"
            assert decrypt_field(encrypt_field(original)) == original

    def test_decrypt_none_returns_none(self, app):
        """valor None → devuelve None."""
        with app.app_context():
            from app.infrastructure.crypto import decrypt_field

            assert decrypt_field(None) is None

    def test_decrypt_corrupted_returns_raw(self, app):
        """Valor corrupto → retorna el valor corrupto (plain-text fallback)."""
        with app.app_context():
            from app.infrastructure.crypto import decrypt_field

            corrupted = "this_is_not_a_valid_fernet_token"
            assert decrypt_field(corrupted) == corrupted


# ---------------------------------------------------------------------------
# hash_field
# ---------------------------------------------------------------------------


class TestHashField:
    def test_hash_returns_64_char_hex(self, app):
        """Retorna HMAC-SHA256 en hex (64 caracteres)."""
        with app.app_context():
            from app.infrastructure.crypto import hash_field

            result = hash_field("my_value")
            assert isinstance(result, str)
            assert len(result) == 64
            int(result, 16)  # valid hex

    def test_hash_none_returns_none(self, app):
        """valor None → devuelve None."""
        with app.app_context():
            from app.infrastructure.crypto import hash_field

            assert hash_field(None) is None

    def test_hash_deterministic(self, app):
        """Mismo input siempre produce el mismo hash."""
        with app.app_context():
            from app.infrastructure.crypto import hash_field

            assert hash_field("same") == hash_field("same")

    def test_hash_different_inputs_different_hashes(self, app):
        """Inputs distintos producen hashes distintos."""
        with app.app_context():
            from app.infrastructure.crypto import hash_field

            assert hash_field("value_a") != hash_field("value_b")
