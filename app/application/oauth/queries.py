from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.enums import OAuthProviderEnum


@dataclass
class GenerateOAuthLoginUrlQuery:
    provider: OAuthProviderEnum


@dataclass
class GetOAuthConnectedAccountsQuery:
    current_channel_id: UUID
