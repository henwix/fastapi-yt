from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.utils.datetime import get_current_utc_datetime
from app.utils.videos import generate_video_id


@dataclass(kw_only=True)
class Video(BaseEntity):
    id: str = field(default_factory=generate_video_id)
    channel_id: UUID
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    is_reported: bool = False
    created_at: datetime = field(default_factory=get_current_utc_datetime)
    views_count: int = 0
    upload_id: str | None = None
    s3_key: str | None = None
    upload_status: VideoUploadStatusEnum = VideoUploadStatusEnum.PENDING

    @staticmethod
    def create(
        channel_id: UUID,
        title: str,
        description: str,
        privacy_status: VideoPrivacyStatusEnum,
    ) -> Video:
        return Video(
            channel_id=channel_id,
            title=title,
            description=description,
            privacy_status=privacy_status,
        )

    def set_title(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.title = value

    def set_description(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.description = value

    def set_privacy_status(self, value: VideoPrivacyStatusEnum | Empty) -> None:
        if value is not Empty.UNSET:
            self.privacy_status = value

    def set_upload_status(self, value: VideoUploadStatusEnum | Empty) -> None:
        if value is not Empty.UNSET:
            self.upload_status = value

    def set_upload_id(self, value: str | None | Empty) -> None:
        if value is not Empty.UNSET:
            self.upload_id = value

    def set_s3_key(self, value: str | None | Empty) -> None:
        if value is not Empty.UNSET:
            self.s3_key = value
