from dataclasses import dataclass
from typing import NoReturn

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.video_views.constants import VIDEO_VIEWS_LIMIT_PER_DAY
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
            case 'video_views_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=video_view.channel_id)
            case _:
                raise

    async def upsert(self, video_view: VideoView) -> bool:
        stmt = insert(VideoViewORM).values(
            id=video_view.id,
            video_id=video_view.video_id,
            channel_id=video_view.channel_id,
            anonymous_id=video_view.anonymous_id,
            views_count=video_view.views_count,
            created_at=video_view.created_at,
        )

        if video_view.channel_id is not None:
            stmt = stmt.on_conflict_do_update(
                index_elements=[VideoViewORM.video_id, VideoViewORM.channel_id, VideoViewORM.created_at],
                index_where=VideoViewORM.channel_id.is_not(None),
                set_={'views_count': VideoViewORM.views_count + 1},
                where=VideoViewORM.views_count < VIDEO_VIEWS_LIMIT_PER_DAY,
            )
        elif video_view.anonymous_id is not None:
            stmt = stmt.on_conflict_do_update(
                index_elements=[VideoViewORM.video_id, VideoViewORM.anonymous_id, VideoViewORM.created_at],
                index_where=VideoViewORM.anonymous_id.is_not(None),
                set_={'views_count': VideoViewORM.views_count + 1},
                where=VideoViewORM.views_count < VIDEO_VIEWS_LIMIT_PER_DAY,
            )
        stmt = stmt.returning(VideoViewORM.id)

        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, video_view=video_view)

        return result.scalar_one_or_none() is not None
