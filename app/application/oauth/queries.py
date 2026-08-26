from dataclasses import dataclass

from app.domain.oauth.enums import OAuthProvidersEnum


@dataclass
class OAuthGetLoginUrlQuery:
    provider: OAuthProvidersEnum
