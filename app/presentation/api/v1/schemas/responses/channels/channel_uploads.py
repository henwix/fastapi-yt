from uuid import UUID

from pydantic import HttpUrl

from app.presentation.api.v1.schemas.base import BaseSchema


class GenerateChannelAvatarUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl
    key: str
    channel_id: UUID
