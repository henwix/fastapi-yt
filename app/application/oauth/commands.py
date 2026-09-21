from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.enums import OAuthProviderEnum


@dataclass(kw_only=True, frozen=True)
class VerifyOAuthCodeCommand:
    current_channel_id: UUID | None
    provider: OAuthProviderEnum
    code: str
    state: str


@dataclass(kw_only=True, frozen=True)
class DisconnectOAuthAccountCommand:
    current_channel_id: UUID
    provider: OAuthProviderEnum
