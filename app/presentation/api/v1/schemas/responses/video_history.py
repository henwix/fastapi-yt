from datetime import datetime

from pydantic import HttpUrl

from app.application.video_history.dto import PreviewVideoHistory
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class PreviewVideoHistoryOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    watched_at: datetime
    author_name: str
    author_slug: str

    @staticmethod
    def from_dto(dto: PreviewVideoHistory) -> PreviewVideoHistoryOutSchema:
        return PreviewVideoHistoryOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            views_count=dto.views_count,
            watched_at=dto.watched_at,
            author_name=dto.author_name,
            author_slug=dto.author_slug,
        )


class VideoHistoryCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PreviewVideoHistoryOutSchema]
