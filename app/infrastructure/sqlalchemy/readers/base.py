from dataclasses import dataclass

from app.infrastructure.sqlalchemy.database import Database


@dataclass
class SQLAlchemyReader:
    _db: Database
