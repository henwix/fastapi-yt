from sqlalchemy import RowMapping

from app.application.videos.dto import DetailedVideoDTO, PersonalPreviewVideoDTO
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum


def convert_row_to_detailed_video_dto(row: RowMapping) -> DetailedVideoDTO:
    return DetailedVideoDTO(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        privacy_status=VideoPrivacyStatusEnum(row['privacy_status']),
        is_reported=row['is_reported'],
        created_at=row['created_at'],
        views_count=row['views_count'],
        channel_id=row['channel_id'],
        channel_name=row['channel_name'],
        channel_slug=row['channel_slug'],
    )


def convert_row_to_personal_preview_video_dto(row: RowMapping) -> PersonalPreviewVideoDTO:
    return PersonalPreviewVideoDTO(
        id=row['id'],
        title=row['title'],
        privacy_status=VideoPrivacyStatusEnum(row['privacy_status']),
        upload_status=VideoUploadStatusEnum(row['upload_status']),
        created_at=row['created_at'],
        views_count=row['views_count'],
    )
