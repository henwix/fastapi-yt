from datetime import datetime

from pydantic import Field, HttpUrl

from app.application.videos.dto import DetailedVideoDTO
from app.domain.common.constants import FILENAME_PATTERN
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class CreateVideoMultipartUploadInSchema(BaseSchema):
    title: str = Field(min_length=1, max_length=100)
    description: str = ''
    privacy_status: VideoPrivacyStatusEnum
    filename: str = Field(max_length=100, pattern=FILENAME_PATTERN, examples=['video.mp4'])


class CreateVideoMultipartUploadOutSchema(BaseSchema):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    upload_id: str
    s3_key: str

    @staticmethod
    def from_entity(entity: Video) -> CreateVideoMultipartUploadOutSchema:
        return CreateVideoMultipartUploadOutSchema(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            privacy_status=entity.privacy_status,
            upload_id=entity.upload_id,
            s3_key=entity.s3_key,
        )


class AbortVideoMultipartUploadInSchema(BaseSchema):
    key: str
    upload_id: str


class GenerateVideoPartUploadUrlInSchema(BaseSchema):
    key: str
    upload_id: str
    part_number: int = Field(ge=1, le=10000)


class GenerateVideoPartUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl


class GenerateVideoDownloadUrlOutSchema(BaseSchema):
    download_url: HttpUrl


class DetailedVideoSchema(BaseSchema):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    s3_key: str
    is_reported: bool
    created_at: datetime
    channel_name: str
    channel_slug: str

    @staticmethod
    def from_dto(dto: DetailedVideoDTO) -> DetailedVideoSchema:
        return DetailedVideoSchema(
            id=dto.id,
            title=dto.title,
            description=dto.description,
            privacy_status=dto.privacy_status,
            s3_key=dto.s3_key,
            is_reported=dto.is_reported,
            created_at=dto.created_at,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
        )
