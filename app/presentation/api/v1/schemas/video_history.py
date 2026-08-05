from datetime import datetime

from pydantic import HttpUrl

from app.application.common.sorting import SortingOrderEnum
from app.application.video_history.dto import PreviewVideoHistoryDTO
from app.application.video_history.queries import VideoHistorySortingFieldsEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class VideoHistorySortingParams(BaseSchema):
    sort_by: VideoHistorySortingFieldsEnum = VideoHistorySortingFieldsEnum.WATCHED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class PreviewVideoHistoryOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    watched_at: datetime
    author_name: str
    author_slug: str

    @staticmethod
    def from_dto(dto: PreviewVideoHistoryDTO) -> PreviewVideoHistoryOutSchema:
        return PreviewVideoHistoryOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            watched_at=dto.watched_at,
            author_name=dto.author_name,
            author_slug=dto.author_slug,
        )


class VideoHistoryCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PreviewVideoHistoryOutSchema]
