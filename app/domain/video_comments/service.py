from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.channels.entities import Channel
from app.domain.video_comments.entities import VideoComment
from app.domain.video_comments.exceptions import VideoCommentAccessForbiddenError, VideoCommentNotFoundError
from app.domain.video_comments.repo import IVideoCommentRepo


class IVideoCommentService(ABC):
    @abstractmethod
    async def create(self, video_comment: VideoComment) -> VideoComment: ...

    @abstractmethod
    async def try_get_by_id(self, id: UUID) -> VideoComment: ...

    @abstractmethod
    async def try_get_by_id_and_video_id(self, id: UUID, video_id: str) -> VideoComment: ...

    @abstractmethod
    async def try_delete_by_id(self, id: UUID) -> None: ...

    @abstractmethod
    async def try_update(self, video_comment: VideoComment) -> VideoComment: ...

    @abstractmethod
    def ensure_video_comment_access(self, video_comment: VideoComment, channel: Channel) -> None: ...


@dataclass
class VideoCommentService(IVideoCommentService):
    _repo: IVideoCommentRepo

    async def create(self, video_comment: VideoComment) -> VideoComment:
        return await self._repo.create(video_comment=video_comment)

    async def try_get_by_id(self, id: UUID) -> VideoComment:
        video_comment = await self._repo.get_by_id(id=id)
        if not video_comment:
            raise VideoCommentNotFoundError(id=id)
        return video_comment

    async def try_get_by_id_and_video_id(self, id: UUID, video_id: str) -> VideoComment:
        video_comment = await self._repo.get_by_id_and_video_id(id=id, video_id=video_id)
        if video_comment is None:
            raise VideoCommentNotFoundError(id=id)
        return video_comment

    async def try_delete_by_id(self, id: UUID) -> None:
        is_deleted = await self._repo.delete_by_id(id=id)
        if not is_deleted:
            raise VideoCommentNotFoundError(id=id)

    async def try_update(self, video_comment: VideoComment) -> VideoComment:
        updated_video_comment = await self._repo.update(video_comment=video_comment)
        if not updated_video_comment:
            raise VideoCommentNotFoundError(id=video_comment.id)
        return updated_video_comment

    def ensure_video_comment_access(self, video_comment: VideoComment, channel: Channel) -> None:
        if video_comment.channel_id != channel.id:
            raise VideoCommentAccessForbiddenError(
                video_comment_id=video_comment.id,
                channel_id=channel.id,
            )
