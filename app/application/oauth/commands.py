from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.enums import OAuthProviderEnum


@dataclass
class OAuthConvertCodeCommand:
    current_channel_id: UUID | None
    provider: OAuthProviderEnum
    code: str
    state: str
