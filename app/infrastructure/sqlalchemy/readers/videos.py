from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.dto import DetailedVideoDTO
from app.application.videos.interfaces.reader import IVideoReader
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoNotFoundByIdError
from app.infrastructure.sqlalchemy.converters.videos import convert_video_row_to_detailed_dto
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import VideoORM


@dataclass
class SAVideoReader(IVideoReader):
    _session: AsyncSession

    async def try_get_detailed_by_id(self, id: str) -> DetailedVideoDTO:
        stmt = (
            select(
                VideoORM.id,
                VideoORM.title,
                VideoORM.description,
                VideoORM.privacy_status,
                VideoORM.s3_key,
                VideoORM.is_reported,
                VideoORM.created_at,
                VideoORM.channel_id,
                ChannelORM.name,
                ChannelORM.slug,
            )
            .join(ChannelORM, VideoORM.channel_id == ChannelORM.id)
            .where(VideoORM.id == id, VideoORM.upload_status == VideoUploadStatusEnum.COMPLETED.value)
        )
        result = await self._session.execute(statement=stmt)
        video_row = result.mappings().one_or_none()

        if video_row is None:
            raise VideoNotFoundByIdError(video_id=id)

        return convert_video_row_to_detailed_dto(row=video_row)
