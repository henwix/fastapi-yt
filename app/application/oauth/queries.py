from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.enums import OAuthProviderEnum


@dataclass
class OAuthGetLoginUrlQuery:
    provider: OAuthProviderEnum


@dataclass
class OAuthGetConnectedAccountsQuery:
    current_channel_id: UUID
