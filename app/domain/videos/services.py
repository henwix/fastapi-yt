from abc import ABC, abstractmethod
from dataclasses import dataclass
from mimetypes import guess_type

from app.domain.channels.entities import Channel
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoFileContentTypesEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileFormatError,
    VideoNotFoundByIdError,
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
            raise VideoNotFoundByIdError(video_id=video.id)
        return updated_video

    async def try_get_by_id(self, id: str) -> Video:
        video = await self._repo.get_by_id(id=id)
        if video is None:
            raise VideoNotFoundByIdError(video_id=id)
        return video

    async def try_get_completed_by_id(self, id: str) -> Video:
        video = await self._repo.get_completed_by_id(id=id)
        if video is None:
            raise VideoNotFoundByIdError(video_id=id)
        return video

    async def try_delete_by_id(self, id: str) -> None:
        is_deleted = await self._repo.delete_by_id(id=id)
        if not is_deleted:
            raise VideoNotFoundByIdError(video_id=id)

    def ensure_video_access(self, video: Video, channel: Channel) -> None:
        if video.channel_id != channel.id:
            raise VideoAccessForbiddenError(video_id=video.id, channel_id=channel.id)

    def ensure_video_upload_not_completed(self, video: Video) -> None:
        if video.upload_status is VideoUploadStatusEnum.COMPLETED and video.upload_id is None:
            raise VideoUploadAlreadyCompletedError(video_id=video.id)

    def validate_video_file_format_and_get_content_type(self, value: str) -> str:
        content_type, _ = guess_type(value)
        if content_type is None or content_type not in VideoFileContentTypesEnum:
            raise VideoInvalidFileFormatError(file=value)
        return content_type
