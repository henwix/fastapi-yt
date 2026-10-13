from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.videos.entities import VideoHistoryItem
from app.domain.videos.exceptions import VideoNotFoundError
from app.domain.videos.repos import IVideoHistoryRepo
from app.infrastructure.sqlalchemy.models import VideoHistoryItemORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class VideoHistoryRepo(SQLAlchemyRepo, IVideoHistoryRepo):
    def _parse_db_error(self, error: DBAPIError, video_history_item: VideoHistoryItem) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'video_history_items_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=video_history_item.channel_id) from error
            case 'video_history_items_video_id_fkey':
                raise VideoNotFoundError(video_id=video_history_item.video_id) from error
            case _:
                raise

    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem:
        stmt = (
            insert(VideoHistoryItemORM)
            .values(
                id=video_history_item.id,
                channel_id=video_history_item.channel_id,
                video_id=video_history_item.video_id,
                created_at=video_history_item.created_at,
            )
            .on_conflict_do_update(
                constraint='unique_video_history_item',
                set_={'created_at': video_history_item.created_at},
            )
            .returning(VideoHistoryItemORM)
        )
        async with self._db.get_session(commit=True) as session:
            try:
                result = await session.execute(statement=stmt)
            except IntegrityError as e:
                self._parse_db_error(error=e, video_history_item=video_history_item)
        model = result.scalar_one()
        return model.to_entity()

    async def delete(self, channel_id: UUID, video_id: str) -> bool:
        stmt = delete(VideoHistoryItemORM).where(
            VideoHistoryItemORM.channel_id == channel_id,
            VideoHistoryItemORM.video_id == video_id,
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def clear(self, channel_id: UUID) -> bool:
        stmt = delete(VideoHistoryItemORM).where(VideoHistoryItemORM.channel_id == channel_id)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0
