from dataclasses import dataclass

from fastapi import Request

from app.application.common.dto import DTO
from app.presentation.api.v1.schemas.base import BaseCursorResponse


@dataclass
class CursorPaginator:
    request: Request

    def get_response(
        self,
        results: list[DTO],
        cursor: str | None,
        response_schema: type[BaseCursorResponse],
    ) -> BaseCursorResponse:
        next_page = None
        if cursor:
            next_page = str(self.request.url.include_query_params(cursor=cursor))

        return response_schema(next_page=next_page, results=results)
