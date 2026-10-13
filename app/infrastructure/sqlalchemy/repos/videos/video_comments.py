from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.videos.entities import VideoComment
from app.domain.videos.exceptions import VideoCommentNotFoundError, VideoNotFoundError
from app.domain.videos.repos import IVideoCommentRepo
from app.infrastructure.sqlalchemy.models import VideoCommentORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class VideoCommentRepo(SQLAlchemyRepo, IVideoCommentRepo):
    def _parse_db_error(self, error: DBAPIError, video_comment: VideoComment) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'video_comments_video_id_fkey':
                raise VideoNotFoundError(video_id=video_comment.video_id) from error
            case 'video_comments_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=video_comment.channel_id) from error
            case 'video_comments_reply_comment_id_fkey':
                raise VideoCommentNotFoundError(video_comment_id=video_comment.reply_comment_id) from error
            case _:
                raise

    async def create(self, video_comment: VideoComment) -> VideoComment:
        model = VideoCommentORM.from_entity(entity=video_comment)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, video_comment=video_comment)
        return model.to_entity()

    async def get_by_id(self, id: UUID) -> VideoComment | None:
        stmt = select(VideoCommentORM).where(VideoCommentORM.id == id)
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        video_comment = result.scalar_one_or_none()
        return video_comment.to_entity() if video_comment else None

    async def get_by_id_and_video_id(self, id: UUID, video_id: str) -> VideoComment | None:
        stmt = select(VideoCommentORM).where(VideoCommentORM.id == id, VideoCommentORM.video_id == video_id)
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        video_comment = result.scalar_one_or_none()
        return video_comment.to_entity() if video_comment else None

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = delete(VideoCommentORM).where(VideoCommentORM.id == id)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def update(self, video_comment: VideoComment) -> VideoComment | None:
        stmt = (
            update(VideoCommentORM)
            .where(VideoCommentORM.id == video_comment.id)
            .values(text=video_comment.text, is_edited=video_comment.is_edited)
            .returning(VideoCommentORM)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        updated_video_comment = result.scalar_one_or_none()
        return updated_video_comment.to_entity() if updated_video_comment else None
