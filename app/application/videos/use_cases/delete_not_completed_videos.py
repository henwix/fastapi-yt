from dataclasses import dataclass
from logging import getLogger

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.videos.repo import IVideoRepo

logger = getLogger(__name__)


@dataclass
class DeleteNotCompletedVideosUseCase:
    _repo: IVideoRepo
    _transaction_manager: ITransactionManager

    async def execute(self) -> int:
        logger.info('Start deleting old videos')
        async with self._transaction_manager:
            result = await self._repo.delete_not_completed_videos()
        logger.info('Complete deleting old videos', extra={'log_meta': {'videos_deleted': result}})
        return result
