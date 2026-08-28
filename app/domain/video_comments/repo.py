from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.video_comments.entities import VideoComment


class IVideoCommentRepo(ABC):
    @abstractmethod
    async def create(self, video_comment: VideoComment) -> VideoComment: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> VideoComment | None: ...

    @abstractmethod
    async def get_by_id_and_video_id(self, id: UUID, video_id: str) -> VideoComment | None: ...

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> bool: ...

    @abstractmethod
    async def update(self, video_comment: VideoComment) -> VideoComment | None: ...
