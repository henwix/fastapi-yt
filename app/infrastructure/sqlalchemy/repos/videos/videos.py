from datetime import timedelta
from typing import NoReturn, cast

from sqlalchemy import CursorResult, delete, exists, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoUploadStatusEnum
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
            .where(VideoORM.id == video.id)
            .values(
                title=video.title,
                description=video.description,
                privacy_status=video.privacy_status,
                upload_id=video.upload_id,
                upload_status=video.upload_status.value,
                s3_key=video.s3_key,
                thumbnail_s3_key=video.thumbnail_s3_key,
            )
            .returning(VideoORM)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        updated_video = result.scalar_one_or_none()
        return updated_video.to_entity() if updated_video else None

    async def increase_views_count(self, video_id: str) -> bool:
        stmt = update(VideoORM).where(VideoORM.id == video_id).values(views_count=VideoORM.views_count + 1)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def get_by_id(self, id: str) -> Video | None:
        stmt = select(VideoORM).where(VideoORM.id == id)
        return await self._get_one_by_query(query=stmt)

    async def get_completed_by_id(self, id: str) -> Video | None:
        stmt = select(VideoORM).where(
            VideoORM.id == id,
            VideoORM.upload_status == VideoUploadStatusEnum.COMPLETED.value,
            exists().where(ChannelORM.id == VideoORM.channel_id, ChannelORM.deleted_at.is_(None)),
        )
        return await self._get_one_by_query(query=stmt)

    async def delete_by_id(self, id: str) -> bool:
        stmt = delete(VideoORM).where(VideoORM.id == id)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def delete_not_completed_videos(self) -> int:
        stmt = delete(VideoORM).where(
            VideoORM.upload_status != VideoUploadStatusEnum.COMPLETED,
            VideoORM.created_at < get_current_utc_datetime() - timedelta(days=7),
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount
