from pydantic import HttpUrl

from app.presentation.api.v1.schemas.base import BaseSchema


class CursorPaginationResponse[TResult: BaseSchema](BaseSchema):
    next_page: HttpUrl | None
    results: list[TResult]
