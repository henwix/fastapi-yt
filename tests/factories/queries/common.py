from datetime import UTC
from random import Random
from uuid import uuid7

from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.common.pagination import CursorPagination
from app.domain.common.constants import Empty
from app.utils.base64url import base64url_encode


class CursorPaginationFactory(DataclassFactory[CursorPagination]):
    __model__ = CursorPagination
    __faker__ = Faker()
    __random = Random()

    @classmethod
    def cursor(cls):
        cursor = base64url_encode(
            value={
                'id': str(uuid7()),
                'created_at': cls.__faker__.date_time(UTC).isoformat(),
            }
        )
        return cls.__random.choice([cursor, Empty.UNSET])
