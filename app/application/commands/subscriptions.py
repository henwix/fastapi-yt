from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class SubscribeCommand:
    current_channel_id: UUID
    channel_slug: str


@dataclass(kw_only=True, frozen=True)
class UnsubscribeCommand:
    current_channel_id: UUID
    channel_slug: str
