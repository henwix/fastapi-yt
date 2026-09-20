from uuid import UUID

from pydantic import HttpUrl

from app.presentation.api.v1.schemas.base import BaseSchema


class GenerateVideoPartUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl


class GenerateVideoDownloadUrlOutSchema(BaseSchema):
    download_url: HttpUrl


class GenerateVideoThumbnailUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl
    key: str
    channel_id: UUID
    video_id: str
