from abc import ABC, abstractmethod

from app.domain.videos.entities import VideoView


class IVideoViewRepo(ABC):
    @abstractmethod
    async def upsert(self, video_view: VideoView) -> bool: ...
