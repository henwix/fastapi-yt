from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.posts.entities import Post
from app.domain.posts.repositories import IPostRepository
from app.infrastructure.sqlalchemy.models.posts import PostORM


@dataclass
class SAPostRepository(IPostRepository):
    _session: AsyncSession

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
