from datetime import UTC, datetime

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.infrastructure.sqlalchemy.models import PostCommentORM, PostORM
from tests.factories.base import BaseORMFactory


class PostORMFactory(BaseORMFactory[PostORM], SQLAlchemyFactory[PostORM]):
    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def updated_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)


class PostCommentORMFactory(BaseORMFactory[PostCommentORM], SQLAlchemyFactory[PostCommentORM]):
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
