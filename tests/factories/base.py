from random import Random

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession


class BaseORMFactory[FT]:
    __set_relationships__ = False
    __faker__ = Faker()
    __random__ = Random()

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> FT:
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.commit()
        return obj

    @classmethod
    async def create_batch(cls, session: AsyncSession, size: int, **kwargs) -> list[FT]:
        objects = cls.batch(size=size, **kwargs)
        session.add_all(objects)
        await session.commit()
        return objects
