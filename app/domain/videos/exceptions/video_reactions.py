from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class VideoReactionNotFoundError(AppError):
    message = 'Video reaction not found'
    video_id: str
    channel_id: UUID
