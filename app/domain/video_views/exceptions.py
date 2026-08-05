from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoViewsLimitReached(AppException):
    message = 'Video views limit reached'

    video_id: str
    channel_id: UUID | None
    anonymous_id: UUID | None
