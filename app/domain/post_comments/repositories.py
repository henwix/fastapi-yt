from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.post_comments.entities import PostComment


class IPostCommentRepository(ABC):
    @abstractmethod
    async def create(self, post_comment: PostComment) -> PostComment: ...

    @abstractmethod
    async def get_by_id_and_post_id(self, id: UUID, post_id: UUID) -> PostComment | None: ...
