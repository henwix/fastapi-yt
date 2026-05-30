from abc import ABC, abstractmethod


class IJWTService(ABC):
    @abstractmethod
    def create_access_token(self, sub: str) -> str: ...

    @abstractmethod
    def create_refresh_token(self, sub: str) -> str: ...

    @abstractmethod
    def create_tokens(self, sub: int) -> dict[str, str]: ...

    @abstractmethod
    def decode_access_token(self, token: str) -> dict: ...

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict: ...
