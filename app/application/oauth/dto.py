from dataclasses import dataclass

from app.application.common.dto import DTO
from app.domain.oauth.enums import OAuthProvidersEnum


@dataclass(kw_only=True, frozen=True)
class OAuthProviderUserData(DTO):
    uid: str
    email: str
    login: str
    name: str
    provider: OAuthProvidersEnum
