from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.enums import OAuthProviderEnum


@dataclass(kw_only=True)
class OAuthVerifyCodeCommand:
    current_channel_id: UUID | None
    provider: OAuthProviderEnum
    code: str
    state: str


@dataclass(kw_only=True)
class OAuthDisconnectAccountCommand:
    current_channel_id: UUID
    provider: OAuthProviderEnum
