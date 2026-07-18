"""FernetCryptoService — implementación de CryptoService usando Fernet + HMAC."""

from app.domain.user.services import CryptoService
from app.infrastructure.crypto import decrypt_field, encrypt_field, hash_field


class FernetCryptoService(CryptoService):
    def encrypt(self, value: str) -> str:
        return encrypt_field(value)

    def decrypt(self, value: str) -> str:
        return decrypt_field(value)

    def hash_value(self, value: str) -> str:
        return hash_field(value)
