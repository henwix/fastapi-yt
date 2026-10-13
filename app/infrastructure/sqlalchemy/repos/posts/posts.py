from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete, exists, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.posts.entities import Post
from app.domain.posts.repos import IPostRepo
from app.infrastructure.sqlalchemy.models import ChannelORM, PostORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class PostRepo(SQLAlchemyRepo, IPostRepo):
    def _parse_db_error(self, error: DBAPIError, post: Post) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'posts_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=post.channel_id) from error
            case _:
                raise

    async def create(self, post: Post) -> Post:
        model = PostORM.from_entity(entity=post)
        async with self._db.get_session(commit=True) as session:
            session.add(model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, post=post)
        return model.to_entity()

    async def update(self, post: Post) -> Post | None:
        stmt = update(PostORM).where(PostORM.id == post.id).values(text=post.text).returning(PostORM)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        updated_post = result.scalar_one_or_none()
        return updated_post.to_entity() if updated_post else None

    async def get_existing_by_id(self, id: UUID) -> Post | None:
        stmt = select(PostORM).where(
            PostORM.id == id,
            exists().where(ChannelORM.id == PostORM.channel_id, ChannelORM.deleted_at.is_(None)),
        )
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        post = result.scalar_one_or_none()
        return post.to_entity() if post else None

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = delete(PostORM).where(PostORM.id == id)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0
