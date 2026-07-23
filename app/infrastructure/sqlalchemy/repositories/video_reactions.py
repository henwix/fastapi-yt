from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_reactions.exceptions import VideoReactionAlreadyExistsError
from app.domain.video_reactions.repositories import IVideoReactionRepository
from app.infrastructure.sqlalchemy.models.videos import VideoReactionORM


@dataclass
class SAVideoReactionRepository(IVideoReactionRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, video_reaction: VideoReaction) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'unique_channel_video_reaction':
                raise VideoReactionAlreadyExistsError(
                    video_id=video_reaction.video_id,
                    channel_id=video_reaction.channel_id,
                )
            case _:
                raise

    async def get_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> VideoReaction | None:
        stmt = select(VideoReactionORM).where(
            VideoReactionORM.video_id == video_id,
            VideoReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        reaction = result.scalar_one_or_none()
        return reaction.to_entity() if reaction else None

    async def update(self, video_reaction: VideoReaction) -> VideoReaction | None:
        stmt = (
            update(VideoReactionORM)
            .where(VideoReactionORM.id == video_reaction.id)
            .values(reaction_type=video_reaction.reaction_type.value)
            .returning(VideoReactionORM)
        )
        result = await self._session.execute(statement=stmt)
        updated_video_reaction = result.scalar_one_or_none()
        return updated_video_reaction.to_entity() if updated_video_reaction else None

    async def create(self, video_reaction: VideoReaction) -> VideoReaction:
        model = VideoReactionORM.from_entity(entity=video_reaction)
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, video_reaction=video_reaction)
        return model.to_entity()

    async def delete_by_video_id_and_channel_id(self, video_id: str, channel_id: UUID) -> bool:
        stmt = delete(VideoReactionORM).where(
            VideoReactionORM.video_id == video_id,
            VideoReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
