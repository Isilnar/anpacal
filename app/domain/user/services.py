from abc import ABC, abstractmethod


class CryptoService(ABC):
    @abstractmethod
    def encrypt(self, value: str) -> str: ...

    @abstractmethod
    def decrypt(self, value: str) -> str: ...

    @abstractmethod
    def hash_value(self, value: str) -> str: ...


class MailService(ABC):
    @abstractmethod
    def send_credentials(self, email: str, username: str, password: str) -> None: ...
