from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.channels.entities import Channel
from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.exceptions import PostCommentAccessForbiddenError, PostCommentNotFoundByIdError
from app.domain.post_comments.repositories import IPostCommentRepository


class IPostCommentService(ABC):
    @abstractmethod
    async def create(self, post_comment: PostComment) -> PostComment: ...

    @abstractmethod
    async def try_get_by_id(self, id: UUID) -> PostComment: ...

    @abstractmethod
    async def try_get_by_id_and_post_id(self, id: UUID, post_id: UUID) -> PostComment: ...

    @abstractmethod
    async def try_delete_by_id(self, id: UUID) -> None: ...

    @abstractmethod
    async def try_update(self, post_comment: PostComment) -> PostComment: ...

    @abstractmethod
    def ensure_post_comment_access(self, post_comment: PostComment, channel: Channel) -> None: ...


@dataclass
class PostCommentService(IPostCommentService):
    _repo: IPostCommentRepository

    async def create(self, post_comment: PostComment) -> PostComment:
        return await self._repo.create(post_comment=post_comment)

    async def try_get_by_id(self, id: UUID) -> PostComment:
        post_comment = await self._repo.get_by_id(id=id)
        if not post_comment:
            raise PostCommentNotFoundByIdError(id=id)
        return post_comment

    async def try_get_by_id_and_post_id(self, id: UUID, post_id: UUID) -> PostComment:
        post_comment = await self._repo.get_by_id_and_post_id(id=id, post_id=post_id)
        if post_comment is None:
            raise PostCommentNotFoundByIdError(id=id)
        return post_comment

    async def try_delete_by_id(self, id: UUID) -> None:
        is_deleted = await self._repo.delete_by_id(id=id)
        if not is_deleted:
            raise PostCommentNotFoundByIdError(id=id)

    async def try_update(self, post_comment: PostComment) -> PostComment:
        updated_post_comment = await self._repo.update(post_comment=post_comment)
        if not updated_post_comment:
            raise PostCommentNotFoundByIdError(id=post_comment.id)
        return updated_post_comment

    def ensure_post_comment_access(self, post_comment: PostComment, channel: Channel) -> None:
        if post_comment.channel_id != channel.id:
            raise PostCommentAccessForbiddenError(
                post_comment_id=post_comment.id,
                channel_id=channel.id,
            )
