from pydantic import Field

from app.domain.common.constants import FILENAME_MAX_LENGTH, FILENAME_PATTERN
from app.presentation.api.v1.schemas.base import BaseSchema


class CreateVideoMultipartUploadInSchema(BaseSchema):
    filename: str = Field(
        max_length=FILENAME_MAX_LENGTH,
        pattern=FILENAME_PATTERN,
        examples=[
            'video.mp4',
            'video.mov',
            'video.mkv',
            'video.webm',
        ],
    )


class GenerateVideoThumbnailUploadUrlInSchema(BaseSchema):
    filename: str = Field(
        max_length=FILENAME_MAX_LENGTH,
        pattern=FILENAME_PATTERN,
        examples=[
            'video_thumbnail.png',
            'video_thumbnail.jpg',
            'video_thumbnail.jpeg',
            'video_thumbnail.webp',
        ],
    )


class ConfirmVideoThumbnailUploadInSchema(BaseSchema):
    key: str
