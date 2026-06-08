from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetChannelQuery:
    current_channel_id: UUID
