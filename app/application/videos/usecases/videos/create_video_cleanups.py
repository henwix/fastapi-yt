from dataclasses import dataclass
from logging import getLogger
from uuid import UUID

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.dto import CreateVideoCleanupsResult
from app.core.configs import settings
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.services import IVideoService

logger = getLogger(__name__)


@dataclass
class CreateVideoCleanupsUseCase:
    _video_service: IVideoService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _tm: ITransactionManager

    async def execute(self) -> CreateVideoCleanupsResult:
        total_cleanups_created = 0
        total_files_deleted = 0
        total_videos_deleted = 0

        logger.info('Start video cleanups creation')
        while True:
            videos = await self._video_service.get_many_for_cleanup(
                limit=settings.videos_cleanup_batch_limit,
                video_exp_days=settings.video_incomplete_upload_expiration_days,
            )
            if not videos:
                logger.info('No videos found, stop cycle')
                break

            cleanups: list[FileCleanup] = []
            video_file_ids: list[UUID] = []
            thumbnail_file_ids: list[UUID] = []
            video_ids: list[str] = []

            for video in videos:
                video_ids.append(video.id)
                if video.video_file_id is not None:
                    video_file_ids.append(video.video_file_id)
                if video.thumbnail_file_id is not None:
                    thumbnail_file_ids.append(video.thumbnail_file_id)

            logger.info(
                'Found videos and their files',
                extra={
                    'log_meta': {
                        'videos_count': len(video_ids),
                        'video_files': len(video_file_ids),
                        'thumbnail_files': len(thumbnail_file_ids),
                    }
                },
            )
            file_ids: list[UUID] = [*video_file_ids, *thumbnail_file_ids]
            if file_ids:
                files = await self._file_service.get_many_by_ids(ids=file_ids)
                cleanup_entities = [FileCleanup.create(key=file.key, bucket=file.bucket) for file in files]
                cleanups.extend(cleanup_entities)

            async with self._tm.begin(commit=True):
                if cleanups:
                    cleanups_created = await self._file_cleanup_service.upsert_many(cleanups=cleanups)
                    total_cleanups_created += cleanups_created
                    logger.info('FileCleanups created', extra={'log_meta': {'cleanups_count': cleanups_created}})

                if file_ids:
                    files_deleted = await self._file_service.delete_many_by_ids(ids=file_ids)
                    total_files_deleted += files_deleted
                    logger.info('Files deleted', extra={'log_meta': {'files_deleted_count': files_deleted}})

                videos_deleted = await self._video_service.delete_many_by_ids(ids=video_ids)
                total_videos_deleted += videos_deleted
                logger.info('Videos deleted', extra={'log_meta': {'videos_deleted_count': videos_deleted}})

        logger.info(
            'Video cleanups creation completed',
            extra={
                'log_meta': {
                    'total_cleanups_created': total_cleanups_created,
                    'total_files_deleted': total_files_deleted,
                    'total_videos_deleted': total_videos_deleted,
                }
            },
        )
        return CreateVideoCleanupsResult(
            total_cleanups_created=total_cleanups_created,
            total_files_deleted=total_files_deleted,
            total_videos_deleted=total_videos_deleted,
        )
