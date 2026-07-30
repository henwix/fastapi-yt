from dataclasses import dataclass
from typing import NoReturn

from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.video_views.entities import VideoView
from app.domain.video_views.repositories import IVideoViewRepository
from app.domain.videos.exceptions import VideoNotFoundError
from app.infrastructure.sqlalchemy.models.videos import VideoViewORM


@dataclass
class SAVideoViewRepository(IVideoViewRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, video_view: VideoView) -> NoReturn:
        cause = getattr(error.orig, '__cause__', None)
        constraint_name = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'video_views_video_id_fkey':
                raise VideoNotFoundError(video_id=video_view.video_id)
            case _:
                raise

    async def create(self, video_view: VideoView) -> VideoView:
        model = VideoViewORM.from_entity(entity=video_view)
        self._session.add(instance=model)
        try:
            await self._session.flush(objects=(model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, video_view=video_view)
        return model.to_entity()
