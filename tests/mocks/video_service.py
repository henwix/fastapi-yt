from app.domain.videos.exceptions import VideoNotFoundError
from app.domain.videos.repositories import IVideoRepository
from app.domain.videos.services import VideoService


class MockVideoService(VideoService):
    def __init__(self, _repo: IVideoRepository):
        super().__init__(_repo=_repo)
        self.TRY_INCREASE_VIEWS_COUNT_RAISE_ERROR = False

    async def try_increase_views_count(self, video_id: str) -> None:
        if self.TRY_INCREASE_VIEWS_COUNT_RAISE_ERROR:
            raise VideoNotFoundError(video_id=video_id)
        return await super().try_increase_views_count(video_id)
