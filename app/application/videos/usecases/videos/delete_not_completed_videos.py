from dataclasses import dataclass
from logging import getLogger

from app.domain.videos.repos import IVideoRepo

logger = getLogger(__name__)


@dataclass
class DeleteNotCompletedVideosUseCase:
    _repo: IVideoRepo

    async def execute(self) -> int:
        logger.info('Start deleting old videos')
        result = await self._repo.delete_not_completed_videos()
        logger.info('Complete deleting old videos', extra={'log_meta': {'videos_deleted': result}})
        return result
