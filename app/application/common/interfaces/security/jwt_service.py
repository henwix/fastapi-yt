from abc import ABC, abstractmethod

from app.application.common.dto.jwt import JWTAccessToken, JWTRefreshToken, JWTTokenPayload


class IJWTService(ABC):
    @abstractmethod
    def create_access_token(self, sub: str) -> JWTAccessToken: ...

    @abstractmethod
    def create_refresh_token(self, sub: str) -> JWTRefreshToken: ...

    @abstractmethod
    def decode_access_token(self, token: str) -> JWTTokenPayload: ...

    @abstractmethod
    def decode_refresh_token(self, token: str) -> JWTTokenPayload: ...

    @abstractmethod
    def decode_unverified_token(self, token: str) -> dict: ...
