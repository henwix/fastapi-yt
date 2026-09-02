from datetime import UTC, datetime
from random import Random

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.sqlalchemy.models.oauth import OAuthAccountORM


class OAuthAcccountORMFactory(SQLAlchemyFactory[OAuthAccountORM]):
    __faker__ = Faker()
    __random__ = Random()
    __set_relationships__ = False

    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def provider(cls) -> str:
        return cls.__random__.choice(['github', 'google'])

    @classmethod
    def provider_uid(cls) -> str:
        return cls.__faker__.numerify('#' * 30)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> OAuthAccountORM:
        object = cls.build(**kwargs)
        session.add(instance=object)
        await session.commit()
        return object

    @classmethod
    async def create_batch(cls, session: AsyncSession, size: int, **kwargs) -> list[OAuthAccountORM]:
        objects = cls.batch(size=size, **kwargs)
        session.add_all(objects)
        await session.commit()
        return objects
