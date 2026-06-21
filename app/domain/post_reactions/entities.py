from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.common.entities import BaseEntity
from app.domain.common.enums import ReactionTypeEnum
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class PostReaction(BaseEntity):
    post_id: UUID
    channel_id: UUID
    reaction_type: ReactionTypeEnum
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(post_id: UUID, channel_id: UUID, reaction_type: ReactionTypeEnum) -> PostReaction:
        return PostReaction(
            post_id=post_id,
            channel_id=channel_id,
            reaction_type=reaction_type,
        )

    def set_reaction_type(self, reaction_type: ReactionTypeEnum) -> None:
        self.reaction_type = reaction_type
