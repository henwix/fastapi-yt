from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.video_comment_reactions.entities import VideoCommentReaction
from app.domain.video_comment_reactions.repo import IVideoCommentReactionRepo
from app.domain.video_comments.exceptions import VideoCommentNotFoundError
from app.infrastructure.sqlalchemy.models.videos import VideoCommentReactionORM
from app.infrastructure.sqlalchemy.repos.base import SARepo


class SAVideoCommentReactionRepo(SARepo, IVideoCommentReactionRepo):
    def _parse_db_error(self, error: DBAPIError, video_comment_reaction: VideoCommentReaction) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'video_comment_reactions_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=video_comment_reaction.channel_id) from error
            case 'video_comment_reactions_video_comment_id_fkey':
                raise VideoCommentNotFoundError(id=video_comment_reaction.video_comment_id) from error
            case _:
                raise

    async def upsert(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction | None:
        stmt = (
            insert(VideoCommentReactionORM)
            .values(
                id=video_comment_reaction.id,
                video_comment_id=video_comment_reaction.video_comment_id,
                channel_id=video_comment_reaction.channel_id,
                reaction_type=video_comment_reaction.reaction_type.value,
                created_at=video_comment_reaction.created_at,
            )
            .on_conflict_do_update(
                constraint='uq_channel_video_comment_reaction',
                set_={'reaction_type': video_comment_reaction.reaction_type.value},
                where=VideoCommentReactionORM.reaction_type != video_comment_reaction.reaction_type.value,
            )
            .returning(VideoCommentReactionORM)
        )
        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, video_comment_reaction=video_comment_reaction)
        model = result.scalar_one_or_none()
        return model.to_entity() if model is not None else None

    async def get_by_video_comment_id_and_channel_id(
        self,
        video_comment_id: UUID,
        channel_id: UUID,
    ) -> VideoCommentReaction | None:
        stmt = select(VideoCommentReactionORM).where(
            VideoCommentReactionORM.video_comment_id == video_comment_id,
            VideoCommentReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        video_comment_reaction = result.scalar_one_or_none()
        return video_comment_reaction.to_entity() if video_comment_reaction else None

    async def create(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction:
        model = VideoCommentReactionORM.from_entity(entity=video_comment_reaction)
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, video_comment_reaction=video_comment_reaction)
        return model.to_entity()

    async def update(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction | None:
        stmt = (
            update(VideoCommentReactionORM)
            .where(VideoCommentReactionORM.id == video_comment_reaction.id)
            .values(reaction_type=video_comment_reaction.reaction_type.value)
            .returning(VideoCommentReactionORM)
        )
        result = await self._session.execute(statement=stmt)
        updated_video_comment_reaction = result.scalar_one_or_none()
        return updated_video_comment_reaction.to_entity() if updated_video_comment_reaction else None

    async def delete_by_video_comment_id_and_channel_id(self, video_comment_id: UUID, channel_id: UUID) -> bool:
        stmt = delete(VideoCommentReactionORM).where(
            VideoCommentReactionORM.video_comment_id == video_comment_id,
            VideoCommentReactionORM.channel_id == channel_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
