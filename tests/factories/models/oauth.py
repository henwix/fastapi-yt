from datetime import UTC, datetime

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.infrastructure.sqlalchemy.models import OAuthAccountORM
from tests.factories.base import BaseORMFactory


class OAuthAcccountORMFactory(BaseORMFactory[OAuthAccountORM], SQLAlchemyFactory[OAuthAccountORM]):
    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def provider(cls) -> str:
        return cls.__random__.choice(['github', 'google'])

    @classmethod
    def provider_uid(cls) -> str:
        return cls.__faker__.numerify('#' * 30)
