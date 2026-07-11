from pydantic import Field

from app.presentation.api.v1.schemas.base import BaseSchema


class CursorPaginationParams(BaseSchema):
    cursor: str | None = None
    per_page: int = Field(default=25, ge=1, le=100)


class Part(BaseSchema):
    ETag: str
    PartNumber: int = Field(ge=1, le=10000)


class CompleteMultipartUploadSchema(BaseSchema):
    key: str
    upload_id: str
    parts: list[Part] = Field(min_length=1, max_length=10000)
