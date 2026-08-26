from abc import ABC, abstractmethod

from app.domain.video_views.entities import VideoView


class IVideoViewRepository(ABC):
    @abstractmethod
    async def upsert(self, video_view: VideoView) -> bool: ...
