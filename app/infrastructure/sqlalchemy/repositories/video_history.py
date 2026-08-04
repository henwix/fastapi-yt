from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.video_history.entities import VideoHistoryItem
from app.domain.video_history.repositories import IVideoHistoryRepository
from app.domain.videos.exceptions import VideoNotFoundError
from app.infrastructure.sqlalchemy.models.videos import VideoHistoryItemORM


@dataclass
class SAVideoHistoryRepository(IVideoHistoryRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, video_history_item: VideoHistoryItem) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

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
        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, video_history_item=video_history_item)
        model = result.scalar_one()
        return model.to_entity()

    async def delete(self, channel_id: UUID, video_id: str) -> bool:
        stmt = delete(VideoHistoryItemORM).where(
            VideoHistoryItemORM.channel_id == channel_id,
            VideoHistoryItemORM.video_id == video_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0

    async def clear(self, channel_id: UUID) -> bool:
        stmt = delete(VideoHistoryItemORM).where(VideoHistoryItemORM.channel_id == channel_id)
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
