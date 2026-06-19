from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.exceptions import PostCommentNotFoundByIdError
from app.domain.post_comments.repositories import IPostCommentRepository


class IPostCommentService(ABC):
    @abstractmethod
    async def create(self, post_comment: PostComment) -> PostComment: ...

    @abstractmethod
    async def try_get_by_id_and_post_id(self, id: UUID, post_id: UUID) -> PostComment: ...


@dataclass
class PostCommentService(IPostCommentService):
    _repo: IPostCommentRepository

    async def create(self, post_comment: PostComment) -> PostComment:
        return await self._repo.create(post_comment=post_comment)

    async def try_get_by_id_and_post_id(self, id: UUID, post_id: UUID) -> PostComment:
        post_comment = await self._repo.get_by_id_and_post_id(id=id, post_id=post_id)
        if post_comment is None:
            raise PostCommentNotFoundByIdError(id=id)
        return post_comment
