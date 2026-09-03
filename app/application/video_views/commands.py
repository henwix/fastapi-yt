from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class CreateVideoViewCommand:
    current_channel_id: UUID | None
    anonymous_id: UUID
    video_id: str
