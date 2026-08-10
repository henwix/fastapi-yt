from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.post_comment_reactions.entities import PostCommentReaction
from app.domain.post_comment_reactions.repositories import IPostCommentReactionRepository
from app.domain.post_comments.exceptions import PostCommentNotFoundError
from app.infrastructure.sqlalchemy.models.posts import PostCommentReactionORM


@dataclass
class SAPostCommentReactionRepository(IPostCommentReactionRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, post_comment_reaction: PostCommentReaction) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'post_comment_reactions_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=post_comment_reaction.channel_id) from error
            case 'post_comment_reactions_post_comment_id_fkey':
                raise PostCommentNotFoundError(id=post_comment_reaction.post_comment_id) from error
            case _:
                raise

    async def upsert(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction | None:
        stmt = (
            insert(PostCommentReactionORM)
            .values(
                id=post_comment_reaction.id,
                post_comment_id=post_comment_reaction.post_comment_id,
                channel_id=post_comment_reaction.channel_id,
                reaction_type=post_comment_reaction.reaction_type.value,
                created_at=post_comment_reaction.created_at,
            )
            .on_conflict_do_update(
                constraint='unique_channel_post_comment_reaction',
                set_={'reaction_type': post_comment_reaction.reaction_type.value},
                where=PostCommentReactionORM.reaction_type != post_comment_reaction.reaction_type.value,
            )
            .returning(PostCommentReactionORM)
        )
        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, post_comment_reaction=post_comment_reaction)
        model = result.scalar_one_or_none()
        return model.to_entity() if model is not None else None

    async def delete_by_post_comment_id_and_channel_id(self, post_comment_id: UUID, channel_id: UUID) -> bool:
        stmt = delete(PostCommentReactionORM).where(
            PostCommentReactionORM.post_comment_id == post_comment_id,
            PostCommentReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
