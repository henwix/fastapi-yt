from datetime import timedelta
from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, and_, delete, exists, or_, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoDeletionStatusEnum, VideoUploadStatusEnum
from app.domain.videos.repos import IVideoRepo
from app.infrastructure.sqlalchemy.models import ChannelORM, VideoORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo
from app.utils.datetime import get_current_utc_datetime


class VideoRepo(SQLAlchemyRepo, IVideoRepo):
    def _parse_db_error(self, error: DBAPIError, video: Video) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'videos_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=video.channel_id)
            case _:
                raise

    async def _get_one_by_query(self, query) -> Video | None:
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=query)
        video = result.scalar_one_or_none()
        return video.to_entity() if video is not None else None

    async def create(self, video: Video) -> Video:
        model = VideoORM.from_entity(entity=video)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, video=video)
        return model.to_entity()

    async def update(self, video: Video) -> Video | None:
        stmt = (
            update(VideoORM)
            .values(
                title=video.title,
                description=video.description,
                privacy_status=video.privacy_status,
            )
            .where(
                VideoORM.id == video.id,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
            .returning(VideoORM)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        updated_video = result.scalar_one_or_none()
        return updated_video.to_entity() if updated_video else None

    async def update_upload_created(self, id: str, upload_id: str, video_file_id: UUID) -> bool:
        stmt = (
            update(VideoORM)
            .values(
                upload_id=upload_id,
                video_file_id=video_file_id,
                upload_status=VideoUploadStatusEnum.UPLOADING.value,
            )
            .where(
                VideoORM.id == id,
                VideoORM.upload_id.is_(None),
                VideoORM.video_file_id.is_(None),
                VideoORM.upload_status == VideoUploadStatusEnum.PENDING.value,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def update_upload_canceled(self, id: str, upload_id: str, video_file_id: UUID) -> bool:
        stmt = (
            update(VideoORM)
            .values(
                upload_id=None,
                video_file_id=None,
                upload_status=VideoUploadStatusEnum.PENDING.value,
            )
            .where(
                VideoORM.id == id,
                VideoORM.upload_id == upload_id,
                VideoORM.video_file_id == video_file_id,
                VideoORM.upload_status == VideoUploadStatusEnum.UPLOADING.value,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def update_upload_completed(self, id: str, upload_id: str, video_file_id: UUID) -> bool:
        stmt = (
            update(VideoORM)
            .values(
                upload_id=None,
                upload_status=VideoUploadStatusEnum.COMPLETED.value,
            )
            .where(
                VideoORM.id == id,
                VideoORM.upload_id == upload_id,
                VideoORM.video_file_id == video_file_id,
                VideoORM.upload_status == VideoUploadStatusEnum.UPLOADING.value,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def update_thumbnail_file_id(
        self,
        id: str,
        new_thumbnail_file_id: UUID,
        prev_thumbnail_file_id: UUID | None,
    ) -> bool:
        stmt = (
            update(VideoORM)
            .values(
                thumbnail_file_id=new_thumbnail_file_id,
            )
            .where(
                VideoORM.id == id,
                VideoORM.thumbnail_file_id == prev_thumbnail_file_id,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def increase_views_count(self, id: str) -> bool:
        stmt = (
            update(VideoORM)
            .values(views_count=VideoORM.views_count + 1)
            .where(
                VideoORM.id == id,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def get_by_id(self, id: str) -> Video | None:
        stmt = select(VideoORM).where(
            VideoORM.id == id,
            VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
        )
        return await self._get_one_by_query(query=stmt)

    async def get_completed_by_id(self, id: str) -> Video | None:
        stmt = select(VideoORM).where(
            VideoORM.id == id,
            VideoORM.upload_status == VideoUploadStatusEnum.COMPLETED.value,
            VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            exists().where(
                ChannelORM.id == VideoORM.channel_id,
                ChannelORM.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value,
            ),
        )
        return await self._get_one_by_query(query=stmt)

    async def get_many_for_cleanup(self, limit: int, video_exp_days: int) -> list[Video]:
        now = get_current_utc_datetime()
        select_for_update_stmt = (
            select(VideoORM.id)
            .with_for_update(skip_locked=True)
            .where(
                or_(
                    and_(
                        VideoORM.upload_status != VideoUploadStatusEnum.COMPLETED.value,
                        VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
                        VideoORM.created_at < now - timedelta(days=video_exp_days),
                    ),
                    and_(
                        VideoORM.deletion_status == VideoDeletionStatusEnum.DELETED.value,
                        VideoORM.locked_until < now,
                    ),
                )
            )
            .limit(limit=limit)
        )
        stmt = (
            update(VideoORM)
            .values(
                deletion_status=VideoDeletionStatusEnum.DELETED.value,
                locked_until=now + timedelta(minutes=5),
            )
            .where(VideoORM.id.in_(select_for_update_stmt))
            .returning(VideoORM)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        rows = result.scalars()
        return [video.to_entity() for video in rows]

    async def get_many_for_purging(self, channel_ids: list[UUID], limit: int, last_id: str | None) -> list[Video]:
        select_for_update_stmt = (
            select(VideoORM.id)
            .where(VideoORM.channel_id.in_(channel_ids))
            .order_by(VideoORM.id.asc())
            .limit(limit=limit)
        )
        if last_id is not None:
            select_for_update_stmt = select_for_update_stmt.where(VideoORM.id > last_id)
        stmt = (
            update(VideoORM)
            .values(deletion_status=VideoDeletionStatusEnum.PURGING.value)
            .where(VideoORM.id.in_(select_for_update_stmt))
            .returning(VideoORM)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return [video.to_entity() for video in result.scalars()]

    async def soft_delete_by_id(self, id: str) -> bool:
        stmt = (
            update(VideoORM)
            .values(
                deletion_status=VideoDeletionStatusEnum.DELETED.value,
                locked_until=get_current_utc_datetime() + timedelta(minutes=5),
            )
            .where(
                VideoORM.id == id,
                VideoORM.deletion_status == VideoDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def delete_many_by_ids(self, ids: list[str]) -> int:
        stmt = delete(VideoORM).where(VideoORM.id.in_(ids))
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount
