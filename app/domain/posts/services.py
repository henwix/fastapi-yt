from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.channels.entities import Channel
from app.domain.posts.entities import Post
from app.domain.posts.exceptions import PostAccessForbiddenError, PostNotFoundError
from app.domain.posts.repositories import IPostRepository


class IPostService(ABC):
    @abstractmethod
    async def create(self, post: Post) -> Post: ...

    @abstractmethod
    async def try_update(self, post: Post) -> Post: ...

    @abstractmethod
    async def try_get_by_id(self, id: UUID) -> Post: ...

    @abstractmethod
    async def try_delete_by_id(self, id: UUID) -> None: ...

    @abstractmethod
    def ensure_post_access(self, post: Post, channel: Channel) -> None: ...


@dataclass
class PostService(IPostService):
    _post_repo: IPostRepository

    async def create(self, post: Post) -> Post:
        return await self._post_repo.create(post=post)

    async def try_update(self, post: Post) -> Post:
        updated_post = await self._post_repo.update(post=post)
        if not updated_post:
            raise PostNotFoundError
        return updated_post

    async def try_get_by_id(self, id: UUID) -> Post:
        post = await self._post_repo.get_by_id(id=id)
        if not post:
            raise PostNotFoundError
        return post

    async def try_delete_by_id(self, id: UUID) -> None:
        is_deleted = await self._post_repo.delete_by_id(id=id)
        if not is_deleted:
            raise PostNotFoundError

    def ensure_post_access(self, post: Post, channel: Channel) -> None:
        if post.channel_id != channel.id:
            raise PostAccessForbiddenError(post_id=post.id, channel_id=channel.id)
