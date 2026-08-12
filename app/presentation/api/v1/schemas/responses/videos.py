from datetime import datetime

from pydantic import HttpUrl

from app.application.videos.dto import DetailedVideoDTO, PersonalPreviewVideoDTO
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class VideoOutSchema(BaseSchema):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime

    @staticmethod
    def from_entity(entity: Video) -> VideoOutSchema:
        return VideoOutSchema(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            privacy_status=entity.privacy_status,
            created_at=entity.created_at,
        )


class DetailedVideoOutSchema(BaseSchema):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    is_reported: bool
    created_at: datetime
    views_count: int
    channel_name: str
    channel_slug: str

    @staticmethod
    def from_dto(dto: DetailedVideoDTO) -> DetailedVideoOutSchema:
        return DetailedVideoOutSchema(
            id=dto.id,
            title=dto.title,
            description=dto.description,
            privacy_status=dto.privacy_status,
            is_reported=dto.is_reported,
            created_at=dto.created_at,
            views_count=dto.views_count,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
        )


class PreviewVideoOutSchema(BaseSchema):
    id: str
    title: str
    created_at: datetime
    author_name: str
    author_slug: str


class PersonalPreviewVideoOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    upload_status: VideoUploadStatusEnum
    created_at: datetime
    views_count: int

    @staticmethod
    def from_dto(dto: PersonalPreviewVideoDTO) -> PersonalPreviewVideoOutSchema:
        return PersonalPreviewVideoOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            upload_status=dto.upload_status,
            created_at=dto.created_at,
            views_count=dto.views_count,
        )


class PersonalPreviewVideosCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PersonalPreviewVideoOutSchema]


class GenerateVideoPartUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl


class GenerateVideoDownloadUrlOutSchema(BaseSchema):
    download_url: HttpUrl
