from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class GetSubscribersQuery:
    current_channel_id: UUID
