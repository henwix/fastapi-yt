import secrets
from datetime import UTC, datetime

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from pwdlib import PasswordHash
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.infrastructure.sqlalchemy.models import ChannelORM, SubscriptionORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.base import BaseORMFactory

_password_hasher = PasswordHash.recommended()


class ChannelORMFactory(BaseORMFactory[ChannelORM], SQLAlchemyFactory[ChannelORM]):
    @classmethod
    def email(cls) -> str:
        return f'{secrets.token_hex(3)}{cls.__faker__.email()}'

    @classmethod
    def slug(cls) -> str:
        return f'{secrets.token_hex(3)}{cls.__faker__.slug()}'

    @classmethod
    def password_hash(cls) -> str:
        password = cls.__faker__.password()
        return _password_hasher.hash(password=password)

    @classmethod
    def deleted_at(cls) -> None:
        return None

    @classmethod
    def deletion_status(cls) -> str:
        return ChannelDeletionStatusEnum.ACTIVE.value

    @classmethod
    def locked_until(cls) -> None:
        return None

    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def updated_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def is_active(cls) -> bool:
        return True

    @classmethod
    async def create_deleted(cls, session: AsyncSession, **kwargs) -> ChannelORM:
        return await cls.create(
            session=session,
            deleted_at=get_current_utc_datetime(),
            deletion_status=ChannelDeletionStatusEnum.DELETED.value,
            **kwargs,
        )


class SubscriptionORMFactory(BaseORMFactory[SubscriptionORM], SQLAlchemyFactory[SubscriptionORM]):
    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)
