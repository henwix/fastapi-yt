from uuid import UUID

from pydantic import HttpUrl

from app.presentation.api.v1.schemas.base import BaseSchema


class VideoPartUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl


class VideoDownloadUrlOutSchema(BaseSchema):
    download_url: HttpUrl


class VideoThumbnailUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl
    key: str
    channel_id: UUID
    video_id: str
