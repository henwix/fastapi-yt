from pydantic import Field

from app.application.common.sorting import SortingOrderEnum
from app.application.videos.queries import PreviewVideosSortingFieldEnum
from app.domain.common.constants import FILENAME_MAX_LENGTH, FILENAME_PATTERN
from app.domain.videos.constants import VIDEO_DESCRIPTION_MAX_LENGTH, VIDEO_TITLE_MAX_LENGTH, VIDEO_TITLE_MIN_LENGTH
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreateVideoMultipartUploadInSchema(BaseSchema):
    title: str = Field(min_length=VIDEO_TITLE_MIN_LENGTH, max_length=VIDEO_TITLE_MAX_LENGTH)
    description: str = Field(default='', max_length=VIDEO_DESCRIPTION_MAX_LENGTH)
    privacy_status: VideoPrivacyStatusEnum
    filename: str = Field(max_length=FILENAME_MAX_LENGTH, pattern=FILENAME_PATTERN, examples=['video.mp4'])


class UpdateVideoInSchema(BaseUpdateSchema):
    title: str = Field(default='', min_length=VIDEO_TITLE_MIN_LENGTH, max_length=VIDEO_TITLE_MAX_LENGTH)
    description: str = Field(default='', max_length=VIDEO_DESCRIPTION_MAX_LENGTH)
    privacy_status: VideoPrivacyStatusEnum = VideoPrivacyStatusEnum.PUBLIC


class PersonalPreviewVideosFiltersParams(BaseSchema):
    privacy_status: VideoPrivacyStatusEnum | None = None
    upload_status: VideoUploadStatusEnum | None = None


class PreviewVideosSortingParams(BaseSchema):
    sort_by: PreviewVideosSortingFieldEnum = PreviewVideosSortingFieldEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
