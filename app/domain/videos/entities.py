from dataclasses import dataclass, field
from uuid import UUID

from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.utils.videos import generate_video_id


@dataclass(kw_only=True)
class Video:
    id: str = field(default_factory=generate_video_id)
    channel_id: UUID
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    is_reported: bool = False
    upload_id: str | None
    s3_key: str
    upload_status: VideoUploadStatusEnum = VideoUploadStatusEnum.UPLOADING

    def update_after_completed_upload(self) -> None:
        self.upload_id = None
        self.upload_status = VideoUploadStatusEnum.COMPLETED

    @staticmethod
    def create(
        channel_id: UUID,
        title: str,
        description: str,
        privacy_status: VideoPrivacyStatusEnum,
        upload_id: str,
        s3_key: str,
    ) -> Video:
        return Video(
            channel_id=channel_id,
            title=title,
            description=description,
            privacy_status=privacy_status,
            upload_id=upload_id,
            s3_key=s3_key,
        )
