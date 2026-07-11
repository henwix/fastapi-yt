from dataclasses import dataclass

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.videos.entities import Video
from app.domain.videos.repositories import IVideoRepository
from app.infrastructure.sqlalchemy.models.videos import VideoORM


@dataclass
class SAVideoRepository(IVideoRepository):
    _session: AsyncSession

    async def create(self, video: Video) -> Video:
        model = VideoORM.from_entity(entity=video)
        self._session.add(instance=model)
        await self._session.flush(objects=(model,))
        return model.to_entity()

    async def update(self, video: Video) -> Video | None:
        stmt = (
            update(VideoORM)
            .where(VideoORM.id == video.id)
            .values(upload_id=video.upload_id, upload_status=video.upload_status.value)
            .returning(VideoORM)
        )
        result = await self._session.execute(statement=stmt)
        updated_video = result.scalar_one_or_none()
        return updated_video.to_entity() if updated_video else None

    async def get_by_upload_id_and_s3_key(self, upload_id: str, s3_key: str) -> Video | None:
        stmt = select(VideoORM).where(VideoORM.upload_id == upload_id, VideoORM.s3_key == s3_key)
        result = await self._session.execute(statement=stmt)
        video = result.scalar_one_or_none()
        return video.to_entity() if video is not None else None

    async def delete_by_id(self, id: str) -> bool:
        stmt = delete(VideoORM).where(VideoORM.id == id)
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
