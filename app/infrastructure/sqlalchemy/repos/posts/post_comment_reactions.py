from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.posts.entities import PostCommentReaction
from app.domain.posts.exceptions import PostCommentNotFoundError
from app.domain.posts.repos import IPostCommentReactionRepo
from app.infrastructure.sqlalchemy.models import PostCommentReactionORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class PostCommentReactionRepo(SQLAlchemyRepo, IPostCommentReactionRepo):
    def _parse_db_error(self, error: DBAPIError, post_comment_reaction: PostCommentReaction) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

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
        async with self._db.get_session(commit=True) as session:
            try:
                result = await session.execute(statement=stmt)
            except IntegrityError as e:
                self._parse_db_error(error=e, post_comment_reaction=post_comment_reaction)
        model = result.scalar_one_or_none()
        return model.to_entity() if model is not None else None

    async def delete_by_post_comment_id_and_channel_id(self, post_comment_id: UUID, channel_id: UUID) -> bool:
        stmt = delete(PostCommentReactionORM).where(
            PostCommentReactionORM.post_comment_id == post_comment_id,
            PostCommentReactionORM.channel_id == channel_id,
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0
