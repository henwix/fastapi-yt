from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.post_reactions.entities import PostReaction
from app.domain.post_reactions.repository import IPostReactionRepository
from app.domain.posts.exceptions import PostNotFoundError
from app.infrastructure.sqlalchemy.models.posts import PostReactionORM
from app.infrastructure.sqlalchemy.repositories.base import SARepository


class SAPostReactionRepository(SARepository, IPostReactionRepository):
    def _parse_db_error(self, error: DBAPIError, post_reaction: PostReaction) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'post_reactions_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=post_reaction.channel_id) from error
            case 'post_reactions_post_id_fkey':
                raise PostNotFoundError(id=post_reaction.post_id) from error
            case _:
                raise

    async def upsert(self, post_reaction: PostReaction) -> PostReaction | None:
        stmt = (
            insert(PostReactionORM)
            .values(
                id=post_reaction.id,
                post_id=post_reaction.post_id,
                channel_id=post_reaction.channel_id,
                reaction_type=post_reaction.reaction_type.value,
                created_at=post_reaction.created_at,
            )
            .on_conflict_do_update(
                constraint='unique_channel_post_reaction',
                set_={'reaction_type': post_reaction.reaction_type.value},
                where=PostReactionORM.reaction_type != post_reaction.reaction_type.value,
            )
            .returning(PostReactionORM)
        )
        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, post_reaction=post_reaction)
        model = result.scalar_one_or_none()
        return model.to_entity() if model is not None else None

    async def delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> bool:
        stmt = delete(PostReactionORM).where(
            PostReactionORM.post_id == post_id,
            PostReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
