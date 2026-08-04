from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class AddVideoToHistoryCommand:
    current_channel_id: UUID
    video_id: str


@dataclass(kw_only=True, frozen=True)
class DeleteVideoFromHistoryCommand:
    current_channel_id: UUID
    video_id: str


@dataclass(kw_only=True, frozen=True)
class ClearVideoHistoryCommand:
    current_channel_id: UUID
