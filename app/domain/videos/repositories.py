from abc import ABC, abstractmethod

from app.domain.videos.entities import Video


class IVideoRepository(ABC):
    @abstractmethod
    async def create(self, video: Video) -> Video: ...

    @abstractmethod
    async def update(self, video: Video) -> Video | None: ...

    @abstractmethod
    async def get_by_upload_id_and_s3_key(self, upload_id: str, s3_key: str) -> Video | None: ...

    @abstractmethod
    async def get_completed_by_id(self, id: str) -> Video | None: ...

    @abstractmethod
    async def delete_by_id(self, id: str) -> bool: ...
