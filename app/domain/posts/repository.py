from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.posts.entities import Post


class IPostRepository(ABC):
    @abstractmethod
    async def create(self, post: Post) -> Post: ...

    @abstractmethod
    async def update(self, post: Post) -> Post | None: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Post | None: ...

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> bool: ...
