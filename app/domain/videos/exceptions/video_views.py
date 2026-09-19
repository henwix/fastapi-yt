from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class VideoViewsLimitReachedError(AppError):
    message = 'Video views limit reached'

    video_id: str
    channel_id: UUID | None
    anonymous_id: UUID | None
