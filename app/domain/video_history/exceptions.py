from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoNotFoundInHistoryError(AppException):
    message = 'Video not found in history'
    channel_id: UUID
    video_id: str
