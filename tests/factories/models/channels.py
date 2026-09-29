from datetime import UTC, datetime

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from pwdlib import PasswordHash

from app.infrastructure.sqlalchemy.models import ChannelORM, SubscriptionORM
from tests.factories.base import BaseORMFactory

_password_hasher = PasswordHash.recommended()


class ChannelORMFactory(BaseORMFactory[ChannelORM], SQLAlchemyFactory[ChannelORM]):
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
    def deleted_at(cls) -> None:
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


class SubscriptionORMFactory(BaseORMFactory[SubscriptionORM], SQLAlchemyFactory[SubscriptionORM]):
    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)
