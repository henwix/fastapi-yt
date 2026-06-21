from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.domain.post_comments.enums import PostCommentReplyLevelEnum
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class PostComment(BaseEntity):
    post_id: UUID
    channel_id: UUID
    reply_comment_id: UUID | None
    is_edited: bool = False
    text: str
    reply_level: PostCommentReplyLevelEnum
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(
        post_id: UUID,
        channel_id: UUID,
        reply_comment_id: UUID | None,
        text: str,
    ) -> PostComment:
        reply_level = PostCommentReplyLevelEnum.ZERO if reply_comment_id is None else PostCommentReplyLevelEnum.ONE
        return PostComment(
            post_id=post_id,
            channel_id=channel_id,
            reply_comment_id=reply_comment_id,
            text=text,
            reply_level=reply_level,
        )

    def update(self, text: str | Empty) -> None:
        if text is not Empty.UNSET:
            self.text = text

        if not self.is_edited:
            self.is_edited = True
