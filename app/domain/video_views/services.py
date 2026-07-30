from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.video_views.entities import VideoView
from app.domain.video_views.repositories import IVideoViewRepository


class IVideoViewService(ABC):
    @abstractmethod
    async def create(self, video_view: VideoView) -> VideoView: ...


@dataclass
class VideoViewService(IVideoViewService):
    _repo: IVideoViewRepository

    async def create(self, video_view: VideoView) -> VideoView:
        return await self._repo.create(video_view=video_view)
