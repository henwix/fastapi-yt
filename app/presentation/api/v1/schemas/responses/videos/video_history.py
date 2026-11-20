from datetime import datetime

from pydantic import HttpUrl

from app.application.videos.dto import PreviewVideoHistory
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class PreviewVideoHistoryOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    watched_at: datetime
    channel_name: str
    channel_slug: str
    video_thumbnail_url: HttpUrl | None

    @staticmethod
    def from_dto(dto: PreviewVideoHistory) -> PreviewVideoHistoryOutSchema:
        return PreviewVideoHistoryOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            views_count=dto.views_count,
            watched_at=dto.watched_at,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
            video_thumbnail_url=dto.video_thumbnail_url,
        )
