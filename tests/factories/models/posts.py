from datetime import UTC, datetime
from random import Random

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.sqlalchemy.models.posts import PostCommentORM, PostORM


class PostORMFactory(SQLAlchemyFactory[PostORM]):
    __set_relationships__ = False
    __faker__ = Faker()

    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def updated_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> PostORM:
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.commit()
        return obj

    @classmethod
    async def create_batch(cls, session: AsyncSession, size: int, **kwargs) -> list[PostORM]:
        objects = cls.batch(size=size, **kwargs)
        session.add_all(objects)
        await session.commit()
        return objects


class PostCommentORMFactory(SQLAlchemyFactory[PostCommentORM]):
    __set_relationships__ = False
    __faker__ = Faker()
    __random__ = Random()

    @classmethod
    def text(cls) -> str:
        return cls.__faker__.sentence()

    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def updated_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def reply_level(cls) -> int:
        return cls.__random__.choice([0, 1])

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> PostCommentORM:
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.commit()
        return obj
