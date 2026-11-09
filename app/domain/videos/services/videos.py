from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.channels.entities import Channel
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
    VideoUploadNotCreatedError,
)
from app.domain.videos.repos import IVideoRepo


class IVideoService(ABC):
    @abstractmethod
    async def create(self, video: Video) -> Video: ...

    @abstractmethod
    async def try_update(self, video: Video) -> Video: ...

    @abstractmethod
    async def update_upload_created(self, id: str, upload_id: str, video_file_id: UUID) -> bool: ...

    @abstractmethod
    async def update_upload_canceled(self, id: str, upload_id: str, video_file_id: UUID) -> bool: ...

    @abstractmethod
    async def update_upload_completed(self, id: str, upload_id: str, video_file_id: UUID) -> bool: ...

    @abstractmethod
    async def update_thumbnail_file_id(
        self,
        id: str,
        new_thumbnail_file_id: UUID,
        prev_thumbnail_file_id: UUID | None,
    ) -> bool: ...

    @abstractmethod
    async def try_increase_views_count(self, id: str) -> None: ...

    @abstractmethod
    async def try_get_by_id(self, id: str) -> Video: ...

    @abstractmethod
    async def try_get_completed_by_id(self, id: str) -> Video: ...

    @abstractmethod
    async def get_many_for_cleanup(self, limit: int, video_exp_days: int) -> list[Video]: ...

    @abstractmethod
    async def try_soft_delete_by_id(self, id: str) -> None: ...

    @abstractmethod
    async def delete_many_by_ids(self, ids: list[str]) -> int: ...

    @abstractmethod
    def ensure_video_access(self, video: Video, channel: Channel) -> None: ...

    @abstractmethod
    def ensure_video_upload_not_completed(self, video: Video) -> None: ...

    @abstractmethod
    def ensure_video_upload_created(self, video: Video) -> None: ...


@dataclass
class VideoService(IVideoService):
    _repo: IVideoRepo

    async def create(self, video: Video) -> Video:
        return await self._repo.create(video=video)

    async def try_update(self, video: Video) -> Video:
        updated_video = await self._repo.update(video=video)
        if updated_video is None:
            raise VideoNotFoundError(video_id=video.id)
        return updated_video

    async def update_upload_created(self, id: str, upload_id: str, video_file_id: UUID) -> bool:
        return await self._repo.update_upload_created(id=id, upload_id=upload_id, video_file_id=video_file_id)

    async def update_upload_canceled(self, id: str, upload_id: str, video_file_id: UUID) -> bool:
        return await self._repo.update_upload_canceled(id=id, upload_id=upload_id, video_file_id=video_file_id)

    async def update_upload_completed(self, id: str, upload_id: str, video_file_id: UUID) -> bool:
        return await self._repo.update_upload_completed(id=id, upload_id=upload_id, video_file_id=video_file_id)

    async def update_thumbnail_file_id(
        self,
        id: str,
        new_thumbnail_file_id: UUID,
        prev_thumbnail_file_id: UUID | None,
    ) -> bool:
        return await self._repo.update_thumbnail_file_id(
            id=id,
            new_thumbnail_file_id=new_thumbnail_file_id,
            prev_thumbnail_file_id=prev_thumbnail_file_id,
        )

    async def try_increase_views_count(self, id: str) -> None:
        is_views_count_increased = await self._repo.increase_views_count(id=id)
        if not is_views_count_increased:
            raise VideoNotFoundError(video_id=id)

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

    async def try_soft_delete_by_id(self, id: str) -> None:
        is_deleted = await self._repo.soft_delete_by_id(id=id)
        if not is_deleted:
            raise VideoNotFoundError(video_id=id)

    async def get_many_for_cleanup(self, limit: int, video_exp_days: int) -> list[Video]:
        return await self._repo.get_many_for_cleanup(limit=limit, video_exp_days=video_exp_days)

    async def delete_many_by_ids(self, ids: list[str]) -> int:
        return await self._repo.delete_many_by_ids(ids=ids)

    def ensure_video_access(self, video: Video, channel: Channel) -> None:
        if video.channel_id != channel.id:
            raise VideoAccessForbiddenError(video_id=video.id, channel_id=channel.id)

    def ensure_video_upload_not_completed(self, video: Video) -> None:
        if video.upload_status is VideoUploadStatusEnum.COMPLETED:
            raise VideoUploadAlreadyCompletedError(video_id=video.id)

    def ensure_video_upload_created(self, video: Video) -> None:
        if (
            video.upload_status is VideoUploadStatusEnum.PENDING
            or video.upload_id is None
            or video.video_file_id is None
        ):
            raise VideoUploadNotCreatedError(video_id=video.id)
