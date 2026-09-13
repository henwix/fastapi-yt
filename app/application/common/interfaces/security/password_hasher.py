from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    @abstractmethod
    def get_password_hash(self, password: str) -> str: ...

    @abstractmethod
    def verify_password_hash(self, password: str, hash: str | None = None) -> bool: ...
