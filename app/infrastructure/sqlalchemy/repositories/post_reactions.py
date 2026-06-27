from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.post_reactions.entities import PostReaction
from app.domain.post_reactions.exceptions import PostReactionAlreadyExistsError
from app.domain.post_reactions.repositories import IPostReactionRepository
from app.infrastructure.sqlalchemy.models.posts import PostReactionORM


@dataclass
class SAPostReactionRepository(IPostReactionRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, post_reaction: PostReaction) -> NoReturn:
        cause = error.orig.__cause__
        if cause is None:
            raise

        match cause.constraint_name:
            case 'unique_channel_post_reaction':
                raise PostReactionAlreadyExistsError(
                    post_id=post_reaction.post_id,
                    channel_id=post_reaction.channel_id,
                ) from error
            case _:
                raise

    async def create(self, post_reaction: PostReaction) -> PostReaction:
        model = PostReactionORM.from_entity(entity=post_reaction)
        self._session.add(model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, post_reaction=post_reaction)
        return model.to_entity()

    async def get_by_post_id_and_channel_id(
        self,
        post_id: UUID,
        channel_id: UUID,
    ) -> PostReaction | None:
        stmt = select(PostReactionORM).where(
            PostReactionORM.post_id == post_id, PostReactionORM.channel_id == channel_id
        )
        result = await self._session.execute(statement=stmt)
        reaction = result.scalar_one_or_none()
        return reaction.to_entity() if reaction else None

    async def update(self, post_reaction: PostReaction) -> PostReaction | None:
        stmt = (
            update(PostReactionORM)
            .where(PostReactionORM.id == post_reaction.id)
            .values(reaction_type=post_reaction.reaction_type.value)
            .returning(PostReactionORM)
        )
        result = await self._session.execute(statement=stmt)
        updated_post_reaction = result.scalar_one_or_none()
        return updated_post_reaction.to_entity() if updated_post_reaction else None

    async def delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> bool:
        stmt = delete(PostReactionORM).where(
            PostReactionORM.post_id == post_id,
            PostReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
