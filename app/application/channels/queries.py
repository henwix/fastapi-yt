from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True)
class GetChannelQuery:
    current_channel_id: UUID


@dataclass(kw_only=True)
class GetChannelAboutInfoQuery:
    channel_slug: str
