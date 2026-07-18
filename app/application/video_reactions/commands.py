from dataclasses import dataclass
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum


@dataclass(kw_only=True, frozen=True)
class CreateVideoReactionCommand:
    current_channel_id: UUID
    video_id: str
    reaction_type: ReactionTypeEnum


@dataclass(kw_only=True, frozen=True)
class DeleteVideoReactionCommand:
    current_channel_id: UUID
    video_id: str
