import secrets

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.infrastructure.sqlalchemy.models import FileORM
from tests.factories.base import BaseORMFactory


class FileORMFactory(BaseORMFactory[FileORM], SQLAlchemyFactory[FileORM]):
    @classmethod
    def bucket(cls) -> str:
        return f'{secrets.token_hex(4)}_{cls.__faker__.slug()}'[:64]

    @classmethod
    def key(cls) -> str:
        return f'{secrets.token_hex(4)}_{cls.__faker__.slug()}'
