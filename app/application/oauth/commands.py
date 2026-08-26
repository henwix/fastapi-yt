from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.enums import OAuthProvidersEnum


@dataclass
class OAuthConvertCodeCommand:
    current_channel_id: UUID | None
    provider: OAuthProvidersEnum
    code: str
    state: str
