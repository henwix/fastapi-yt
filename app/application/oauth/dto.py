from dataclasses import dataclass
from datetime import datetime

from app.application.common.dto import DTO
from app.domain.oauth.enums import OAuthProviderEnum


@dataclass(kw_only=True, frozen=True)
class OAuthProviderUserData(DTO):
    uid: str
    email: str
    login: str
    name: str
    provider: OAuthProviderEnum


@dataclass(kw_only=True, frozen=True)
class OAuthAccount(DTO):
    provider: OAuthProviderEnum
    created_at: datetime
