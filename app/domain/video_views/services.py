from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.video_views.entities import VideoView
from app.domain.video_views.exceptions import VideoViewsLimitReached
from app.domain.video_views.repositories import IVideoViewRepository


class IVideoViewService(ABC):
    @abstractmethod
    async def try_upsert(self, video_view: VideoView) -> None: ...


@dataclass
class VideoViewService(IVideoViewService):
    _repo: IVideoViewRepository

    async def try_upsert(self, video_view: VideoView) -> None:
        is_view_created = await self._repo.upsert(video_view=video_view)
        if not is_view_created:
            raise VideoViewsLimitReached(
                video_id=video_view.video_id,
                channel_id=video_view.channel_id,
                anonymous_id=video_view.anonymous_id,
            )
