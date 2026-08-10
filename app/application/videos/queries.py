from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.domain.common.constants import Empty
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum


@dataclass(kw_only=True, frozen=True)
class GetVideoQuery:
    current_channel_id: UUID | None
    video_id: str


@dataclass(kw_only=True, frozen=True)
class PersonalVideosFilters:
    privacy_status: VideoPrivacyStatusEnum | Empty = Empty.UNSET
    upload_status: VideoUploadStatusEnum | Empty = Empty.UNSET


class PreviewVideosSortingFieldEnum(StrEnum):
    CREATED_AT = 'created_at'
    POPULAR = 'popular'


@dataclass(kw_only=True, frozen=True)
class PreviewVideosSorting:
    sort_by: PreviewVideosSortingFieldEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPersonalVideosQuery:
    current_channel_id: UUID
    filters: PersonalVideosFilters
    sorting: PreviewVideosSorting
    pagination: CursorPagination
