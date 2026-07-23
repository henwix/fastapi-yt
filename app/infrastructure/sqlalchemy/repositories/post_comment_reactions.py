from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.post_comment_reactions.entities import PostCommentReaction
from app.domain.post_comment_reactions.exceptions import PostCommentReactionAlreadyExistsError
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
            case 'unique_channel_post_comment_reaction':
                raise PostCommentReactionAlreadyExistsError(
                    post_comment_id=post_comment_reaction.post_comment_id,
                    channel_id=post_comment_reaction.channel_id,
                ) from error
            case 'post_comment_reactions_channel_id_fkey':
                raise ChannelNotFoundByIdError(id=post_comment_reaction.channel_id)
            case 'post_comment_reactions_post_comment_id_fkey':
                raise PostCommentNotFoundError(id=post_comment_reaction.post_comment_id)
            case _:
                raise

    async def get_by_post_comment_id_and_channel_id(
        self,
        post_comment_id: UUID,
        channel_id: UUID,
    ) -> PostCommentReaction | None:
        stmt = select(PostCommentReactionORM).where(
            PostCommentReactionORM.post_comment_id == post_comment_id,
            PostCommentReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        post_comment_reaction = result.scalar_one_or_none()
        return post_comment_reaction.to_entity() if post_comment_reaction else None

    async def create(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction:
        model = PostCommentReactionORM.from_entity(entity=post_comment_reaction)
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, post_comment_reaction=post_comment_reaction)
        return model.to_entity()

    async def update(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction | None:
        stmt = (
            update(PostCommentReactionORM)
            .where(PostCommentReactionORM.id == post_comment_reaction.id)
            .values(reaction_type=post_comment_reaction.reaction_type.value)
            .returning(PostCommentReactionORM)
        )
        result = await self._session.execute(statement=stmt)
        updated_post_comment_reaction = result.scalar_one_or_none()
        return updated_post_comment_reaction.to_entity() if updated_post_comment_reaction else None

    async def delete_by_post_comment_id_and_channel_id(self, post_comment_id: UUID, channel_id: UUID) -> bool:
        stmt = delete(PostCommentReactionORM).where(
            PostCommentReactionORM.post_comment_id == post_comment_id,
            PostCommentReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
