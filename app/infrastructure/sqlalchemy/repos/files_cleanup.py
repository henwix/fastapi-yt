from typing import NoReturn

from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.exceptions import FileCleanupAlreadyCreatedError
from app.domain.files_cleanup.repos import IFileCleanupRepo
from app.infrastructure.sqlalchemy.models import FileCleanupORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class FileCleanupRepo(SQLAlchemyRepo, IFileCleanupRepo):
    def _parse_db_error(self, error: DBAPIError, cleanup: FileCleanup) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'uq_file_cleanup':
                raise FileCleanupAlreadyCreatedError(s3_key=cleanup.s3_key, bucket=cleanup.bucket)
            case _:
                raise

    async def create(self, cleanup: FileCleanup) -> FileCleanup:
        model = FileCleanupORM.from_entity(entity=cleanup)
        self._session.add(instance=model)
        try:
            await self._session.flush(objects=(model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, cleanup=cleanup)
        return model.to_entity()

    async def create_many(self, cleanups: list[FileCleanup]) -> None:
        models = [FileCleanupORM.from_entity(entity=cleanup) for cleanup in cleanups]
        self._session.add_all(instances=models)
        await self._session.flush(objects=models)
