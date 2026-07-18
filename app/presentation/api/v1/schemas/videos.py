from datetime import datetime

from pydantic import Field, HttpUrl

from app.application.common.sorting import SortingOrderEnum
from app.application.videos.dto import DetailedVideoDTO, PersonalVideoDTO
from app.application.videos.queries import GetPersonalVideosSortingFieldEnum
from app.domain.common.constants import FILENAME_MAX_LENGTH, FILENAME_PATTERN
from app.domain.videos.constants import VIDEO_DESCRIPTION_MAX_LENGTH, VIDEO_TITLE_MAX_LENGTH, VIDEO_TITLE_MIN_LENGTH
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class UpdateVideoInSchema(BaseUpdateSchema):
    title: str = Field(default='', min_length=VIDEO_TITLE_MIN_LENGTH, max_length=VIDEO_TITLE_MAX_LENGTH)
    description: str = Field(default='', max_length=VIDEO_DESCRIPTION_MAX_LENGTH)
    privacy_status: VideoPrivacyStatusEnum = VideoPrivacyStatusEnum.PUBLIC


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
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
        )


class PersonalVideosFiltersParams(BaseSchema):
    privacy_status: VideoPrivacyStatusEnum | None = None
    upload_status: VideoUploadStatusEnum | None = None


class PersonalVideosSortingParams(BaseSchema):
    sort_by: GetPersonalVideosSortingFieldEnum = GetPersonalVideosSortingFieldEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class PersonalVideoPreviewOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    upload_status: VideoUploadStatusEnum
    created_at: datetime

    @staticmethod
    def from_dto(dto: PersonalVideoDTO) -> PersonalVideoPreviewOutSchema:
        return PersonalVideoPreviewOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            upload_status=dto.upload_status,
            created_at=dto.created_at,
        )


class PersonalVideosCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PersonalVideoPreviewOutSchema]


class CreateVideoMultipartUploadInSchema(BaseSchema):
    title: str = Field(min_length=VIDEO_TITLE_MIN_LENGTH, max_length=VIDEO_TITLE_MAX_LENGTH)
    description: str = Field(default='', max_length=VIDEO_DESCRIPTION_MAX_LENGTH)
    privacy_status: VideoPrivacyStatusEnum
    filename: str = Field(max_length=FILENAME_MAX_LENGTH, pattern=FILENAME_PATTERN, examples=['video.mp4'])


class GenerateVideoPartUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl


class GenerateVideoDownloadUrlOutSchema(BaseSchema):
    download_url: HttpUrl
