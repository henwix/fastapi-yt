from dataclasses import dataclass

from fastapi import Request

from app.domain.common.entities import BaseEntity
from app.presentation.api.v1.schemas.base import BaseCursorResponse
from app.utils.base64url import base64url_encode_cursor


@dataclass
class CursorPaginator:
    request: Request

    def get_response(
        self,
        results: list[BaseEntity],
        cursor: dict,
        response_schema: type[BaseCursorResponse],
    ) -> BaseCursorResponse:
        next_page = None
        if cursor:
            encoded_cursor = base64url_encode_cursor(cursor)
            next_page = str(self.request.url.include_query_params(cursor=encoded_cursor))

        return response_schema(next_page=next_page, results=results)
