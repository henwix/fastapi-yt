from dataclasses import dataclass

from sqlalchemy.exc import DBAPIError

from app.infrastructure.sqlalchemy.database import Database


@dataclass
class SQLAlchemyRepo:
    _db: Database

    def _extract_constraint_name(self, error: DBAPIError) -> str:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise
        return constraint_name
