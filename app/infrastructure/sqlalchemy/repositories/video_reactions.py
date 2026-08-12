from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_reactions.repositories import IVideoReactionRepository
from app.domain.videos.exceptions import VideoNotFoundError
from app.infrastructure.sqlalchemy.models.videos import VideoReactionORM
from app.infrastructure.sqlalchemy.repositories.base import SARepository


class SAVideoReactionRepository(SARepository, IVideoReactionRepository):
    def _parse_db_error(self, error: DBAPIError, video_reaction: VideoReaction) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'video_reactions_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=video_reaction.channel_id) from error
            case 'video_reactions_video_id_fkey':
                raise VideoNotFoundError(video_id=video_reaction.video_id) from error
            case _:
                raise

    async def upsert(self, video_reaction: VideoReaction) -> VideoReaction | None:
        stmt = (
            insert(VideoReactionORM)
            .values(
                id=video_reaction.id,
                video_id=video_reaction.video_id,
                channel_id=video_reaction.channel_id,
                reaction_type=video_reaction.reaction_type.value,
                created_at=video_reaction.created_at,
            )
            .on_conflict_do_update(
                constraint='unique_channel_video_reaction',
                set_={'reaction_type': video_reaction.reaction_type.value},
                where=VideoReactionORM.reaction_type != video_reaction.reaction_type.value,
            )
            .returning(VideoReactionORM)
        )
        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, video_reaction=video_reaction)
        model = result.scalar_one_or_none()
        return model.to_entity() if model is not None else None

    async def delete_by_video_id_and_channel_id(self, video_id: str, channel_id: UUID) -> bool:
        stmt = delete(VideoReactionORM).where(
            VideoReactionORM.video_id == video_id,
            VideoReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
