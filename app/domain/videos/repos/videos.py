from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.videos.entities import Video


class IVideoRepo(ABC):
    @abstractmethod
    async def create(self, video: Video) -> Video: ...

    @abstractmethod
    async def update(self, video: Video) -> Video | None: ...

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
    async def increase_views_count(self, id: str) -> bool: ...

    @abstractmethod
    async def get_completed_by_id(self, id: str) -> Video | None: ...

    @abstractmethod
    async def get_by_id(self, id: str) -> Video | None: ...

    @abstractmethod
    async def get_many_for_cleanup(self, limit: int, video_exp_days: int) -> list[Video]: ...

    @abstractmethod
    async def get_many_for_purging(self, channel_ids: list[UUID], limit: int, last_id: str | None) -> list[Video]: ...

    @abstractmethod
    async def soft_delete_by_id(self, id: str) -> bool: ...

    @abstractmethod
    async def delete_many_by_ids(self, ids: list[str]) -> int: ...
