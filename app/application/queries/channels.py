from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetChannelQuery:
    channel_id: UUID
