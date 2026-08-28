from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.domain.oauth.enums import OAuthProviderEnum
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class OAuthAccount(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    channel_id: UUID
    provider_uid: str
    provider: OAuthProviderEnum
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(channel_id: UUID, provider_uid: str, provider: OAuthProviderEnum) -> OAuthAccount:
        return OAuthAccount(
            channel_id=channel_id,
            provider_uid=provider_uid,
            provider=provider,
        )
