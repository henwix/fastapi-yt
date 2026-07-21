from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from app.domain.channels.entities import Channel
from app.domain.videos.constants import VIDEO_FILE_MIME_TYPES
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileFormatError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
)
from app.domain.videos.repositories import IVideoRepository


class IVideoService(ABC):
    @abstractmethod
    async def create(self, video: Video) -> Video: ...

    @abstractmethod
    async def try_update(self, video: Video) -> Video: ...

    @abstractmethod
    async def try_get_by_id(self, id: str) -> Video: ...

    @abstractmethod
    async def try_get_completed_by_id(self, id: str) -> Video: ...

    @abstractmethod
    async def try_delete_by_id(self, id: str) -> None: ...

    @abstractmethod
    def ensure_video_access(self, video: Video, channel: Channel) -> None: ...

    @abstractmethod
    def ensure_video_upload_not_completed(self, video: Video) -> None: ...

    @abstractmethod
    def validate_video_file_format_and_get_content_type(self, value: str) -> str: ...


@dataclass
class VideoService(IVideoService):
    _repo: IVideoRepository

    async def create(self, video: Video) -> Video:
        return await self._repo.create(video=video)

    async def try_update(self, video: Video) -> Video:
        updated_video = await self._repo.update(video=video)
        if updated_video is None:
            raise VideoNotFoundError(video_id=video.id)
        return updated_video

    async def try_get_by_id(self, id: str) -> Video:
        video = await self._repo.get_by_id(id=id)
        if video is None:
            raise VideoNotFoundError(video_id=id)
        return video

    async def try_get_completed_by_id(self, id: str) -> Video:
        video = await self._repo.get_completed_by_id(id=id)
        if video is None:
            raise VideoNotFoundError(video_id=id)
        return video

    async def try_delete_by_id(self, id: str) -> None:
        is_deleted = await self._repo.delete_by_id(id=id)
        if not is_deleted:
            raise VideoNotFoundError(video_id=id)

    def ensure_video_access(self, video: Video, channel: Channel) -> None:
        if video.channel_id != channel.id:
            raise VideoAccessForbiddenError(video_id=video.id, channel_id=channel.id)

    def ensure_video_upload_not_completed(self, video: Video) -> None:
        if video.upload_status is VideoUploadStatusEnum.COMPLETED or video.upload_id is None:
            raise VideoUploadAlreadyCompletedError(video_id=video.id)

    def validate_video_file_format_and_get_content_type(self, value: str) -> str:
        content_type = Path(value).suffix.lower()
        if content_type not in VIDEO_FILE_MIME_TYPES:
            raise VideoInvalidFileFormatError(file=value)
        return content_type
