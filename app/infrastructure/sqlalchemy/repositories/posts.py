from dataclasses import dataclass
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.posts.entities import Post
from app.domain.posts.repositories import IPostRepository
from app.infrastructure.sqlalchemy.models.posts import PostORM


@dataclass
class SAPostRepository(IPostRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, post: Post) -> NoReturn:
        cause = getattr(error.orig, '__cause__', None)
        constraint_name = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'posts_channel_id_fkey':
                raise ChannelNotFound

    async def create(self, post: Post) -> Post:
        model = PostORM.from_entity(entity=post)
        self._session.add(model)
        await self._session.flush((model,))
        return model.to_entity()

    async def update(self, post: Post) -> Post | None:
        stmt = update(PostORM).where(PostORM.id == post.id).values(text=post.text).returning(PostORM)
        result = await self._session.execute(statement=stmt)
        updated_post = result.scalar_one_or_none()
        return updated_post.to_entity() if updated_post else None

    async def get_by_id(self, id: UUID) -> Post | None:
        stmt = select(PostORM).where(PostORM.id == id)
        result = await self._session.execute(statement=stmt)
        post = result.scalar_one_or_none()
        return post.to_entity() if post else None

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = delete(PostORM).where(PostORM.id == id)
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
