from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.domain.common.enums import ReactionTypeEnum
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class VideoCommentReaction(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    video_comment_id: UUID
    channel_id: UUID
    reaction_type: ReactionTypeEnum
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(video_comment_id: UUID, channel_id: UUID, reaction_type: ReactionTypeEnum) -> VideoCommentReaction:
        return VideoCommentReaction(
            video_comment_id=video_comment_id,
            channel_id=channel_id,
            reaction_type=reaction_type,
        )
