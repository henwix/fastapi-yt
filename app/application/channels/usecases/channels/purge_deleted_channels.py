from dataclasses import dataclass
from itertools import batched
from logging import getLogger
from uuid import UUID

from app.application.channels.dto import PurgeDeletedChannelsResult
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.services import IVideoService

logger = getLogger(__name__)


@dataclass
class PurgeDeletedChannelsUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _tm: ITransactionManager

    async def execute(self) -> PurgeDeletedChannelsResult:
        total_files_deleted = 0
        total_cleanups_created = 0
        total_channels_deleted = 0

        logger.info('Start channels purging')

        while True:
            channels = await self._channel_service.get_many_for_purging(
                lock_exp_minutes=settings.channels_purging_lock_exp_minutes,
                deletion_retention_days=settings.channel_deletion_retention_days,
                limit=settings.channels_purging_batch_limit,
            )
            if not channels:
                logger.info('No channels for purging found, stop cycle')
                break

            logger.info('Found channels for purging', extra={'log_meta': {'channels_count': len(channels)}})

            channel_ids: list[UUID] = []
            files_ids: set[UUID] = set()

            for channel in channels:
                channel_ids.append(channel.id)
                if channel.avatar_file_id is not None:
                    files_ids.add(channel.avatar_file_id)

            last_video_id: str | None = None
            while True:
                videos = await self._video_service.get_many_for_purging(
                    channel_ids=channel_ids,
                    limit=settings.videos_purging_batch_limit,
                    last_id=last_video_id,
                )
                if not videos:
                    break

                for video in videos:
                    if video.video_file_id is not None:
                        files_ids.add(video.video_file_id)
                    if video.thumbnail_file_id is not None:
                        files_ids.add(video.thumbnail_file_id)

                last_video_id = videos[-1].id

            logger.info('Found files for purging', extra={'log_meta': {'files_count': len(files_ids)}})

            for files_ids_batch in batched(files_ids, settings.files_purging_batch_limit, strict=False):
                files = await self._file_service.get_many_by_ids(ids=list(files_ids_batch))
                cleanups = [FileCleanup.create(key=file.key, bucket=file.bucket) for file in files]
                files_ids_batch = [file.id for file in files]

                async with self._tm.begin(commit=True):
                    file_cleanups_created = await self._file_cleanup_service.upsert_many(cleanups=cleanups)
                    files_deleted = await self._file_service.delete_many_by_ids(ids=files_ids_batch)

                total_files_deleted += files_deleted
                total_cleanups_created += file_cleanups_created

            logger.info('Files were deleted', extra={'log_meta': {'files_count': len(files_ids)}})

            channels_deleted = await self._channel_service.delete_many_by_ids(ids=channel_ids)
            total_channels_deleted += channels_deleted
            logger.info('Channels were deleted', extra={'log_meta': {'channels_count': channels_deleted}})

        logger.info(
            'Channels purging completed',
            extra={
                'log_meta': {
                    'total_files_deleted': total_files_deleted,
                    'total_cleanups_created': total_cleanups_created,
                    'total_channels_deleted': total_channels_deleted,
                }
            },
        )
        return PurgeDeletedChannelsResult(
            total_files_deleted=total_files_deleted,
            total_cleanups_created=total_cleanups_created,
            total_channels_deleted=total_channels_deleted,
        )
