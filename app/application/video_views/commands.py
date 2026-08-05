from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateVideoViewCommand:
    current_channel_id: UUID | None
    anonymous_id: UUID | None
    video_id: str
