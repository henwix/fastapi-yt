from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateVideoViewCommand:
    current_channel_id: UUID
    video_id: str
