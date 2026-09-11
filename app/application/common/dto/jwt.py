from dataclasses import dataclass

from app.application.common.dto.base import DTO


@dataclass(kw_only=True, frozen=True)
class JWTTokens(DTO):
    access: JWTAccessToken
    refresh: JWTRefreshToken


@dataclass(kw_only=True, frozen=True)
class JWTAccessToken(DTO):
    token: str


@dataclass(kw_only=True, frozen=True)
class JWTRefreshToken(DTO):
    token: str
    jti: str


@dataclass(kw_only=True, frozen=True)
class JWTTokenPayload(DTO):
    token_type: str
    sub: str
    jti: str | None
