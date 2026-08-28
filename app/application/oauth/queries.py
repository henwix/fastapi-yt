from dataclasses import dataclass

from app.domain.oauth.enums import OAuthProviderEnum


@dataclass
class OAuthGetLoginUrlQuery:
    provider: OAuthProviderEnum
