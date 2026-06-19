from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.exceptions import PostCommentInvalidReplyLevel, PostCommentNotFoundByIdError
from app.domain.post_comments.repositories import IPostCommentRepository
from app.domain.posts.exceptions import PostNotFoundByIdError
from app.infrastructure.sqlalchemy.models.posts import PostCommentORM


@dataclass
class SAPostCommentRepository(IPostCommentRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, post_comment: PostComment) -> NoReturn:
        cause = error.orig.__cause__
        if cause is None:
            raise

        match cause.constraint_name:
            case 'post_comments_post_id_fkey':
                raise PostNotFoundByIdError(id=post_comment.post_id) from error
            case 'post_comments_channel_id_fkey':
                raise ChannelNotFoundByIdError(id=post_comment.channel_id) from error
            case 'post_comments_reply_comment_id_fkey':
                raise PostCommentNotFoundByIdError(id=post_comment.reply_comment_id) from error
            case 'ck_reply_level':
                raise PostCommentInvalidReplyLevel(reply_level=post_comment.reply_level) from error
            case _:
                raise

    async def create(self, post_comment: PostComment) -> PostComment:
        model = PostCommentORM.from_entity(entity=post_comment)
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, post_comment=post_comment)
        return model.to_entity()

    async def get_by_id_and_post_id(self, id: UUID, post_id: UUID) -> PostComment | None:
        stmt = select(PostCommentORM).where(PostCommentORM.id == id, PostCommentORM.post_id == post_id)
        result = await self._session.execute(statement=stmt)
        post_comment = result.scalar_one_or_none()
        return post_comment.to_entity() if post_comment else None
