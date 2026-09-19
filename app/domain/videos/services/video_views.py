from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.videos.entities import VideoView
from app.domain.videos.exceptions import VideoViewsLimitReachedError
from app.domain.videos.repos import IVideoViewRepo


class IVideoViewService(ABC):
    @abstractmethod
    async def try_upsert(self, video_view: VideoView) -> None: ...


@dataclass
class VideoViewService(IVideoViewService):
    _repo: IVideoViewRepo

    async def try_upsert(self, video_view: VideoView) -> None:
        is_view_created = await self._repo.upsert(video_view=video_view)
        if not is_view_created:
            raise VideoViewsLimitReachedError(
                video_id=video_view.video_id,
                channel_id=video_view.channel_id,
                anonymous_id=video_view.anonymous_id,
            )
