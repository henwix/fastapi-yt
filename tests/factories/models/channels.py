from datetime import UTC, datetime

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.sqlalchemy.models.channels import ChannelORM

_password_hasher = PasswordHash.recommended()


class ChannelORMFactory(SQLAlchemyFactory[ChannelORM]):
    __set_relationships__ = False
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()

    @classmethod
    def slug(cls) -> str:
        return cls.__faker__.slug()

    @classmethod
    def password_hash(cls) -> str:
        password = cls.__faker__.password()
        return _password_hasher.hash(password=password)

    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def updated_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> ChannelORM:
        object = cls.build(**kwargs)
        session.add(instance=object)
        await session.commit()
        return object
