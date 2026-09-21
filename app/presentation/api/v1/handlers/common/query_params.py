from typing import Annotated

from fastapi import Depends

from app.presentation.api.v1.schemas.requests.common import CursorPaginationParamsSchema

CursorPaginationParams = Annotated[CursorPaginationParamsSchema, Depends()]
