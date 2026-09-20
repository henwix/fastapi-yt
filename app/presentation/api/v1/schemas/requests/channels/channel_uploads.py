from pydantic import Field

from app.domain.common.constants import FILENAME_MAX_LENGTH, FILENAME_PATTERN
from app.presentation.api.v1.schemas.base import BaseSchema


class GenerateChannelAvatarUploadUrlInSchema(BaseSchema):
    filename: str = Field(
        max_length=FILENAME_MAX_LENGTH,
        pattern=FILENAME_PATTERN,
        examples=[
            'avatar_image.png',
            'avatar_image.jpg',
            'avatar_image.jpeg',
            'avatar_image.webp',
        ],
    )


class ChannelAvatarUploadConfirmInSchema(BaseSchema):
    key: str
