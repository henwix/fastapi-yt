from sqlalchemy import RowMapping

from app.application.videos.dtos import ChannelPreviewVideo, DetailedVideo, PersonalPreviewVideo
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum


def convert_row_to_detailed_video_dto(row: RowMapping) -> DetailedVideo:
    return DetailedVideo(
        id=row.id,
        title=row.title,
        description=row.description,
        privacy_status=VideoPrivacyStatusEnum(row.privacy_status),
        is_reported=row.is_reported,
        created_at=row.created_at,
        views_count=row.views_count,
        thumbnail_s3_key=row.thumbnail_s3_key,
        channel_id=row.channel_id,
        channel_name=row.channel_name,
        channel_slug=row.channel_slug,
    )


def convert_row_to_channel_preview_video_dto(row: RowMapping) -> ChannelPreviewVideo:
    return ChannelPreviewVideo(
        id=row.id,
        title=row.title,
        views_count=row.views_count,
        thumbnail_s3_key=row.thumbnail_s3_key,
        created_at=row.created_at,
    )


def convert_row_to_personal_preview_video_dto(row: RowMapping) -> PersonalPreviewVideo:
    return PersonalPreviewVideo(
        id=row.id,
        title=row.title,
        privacy_status=VideoPrivacyStatusEnum(row.privacy_status),
        upload_status=VideoUploadStatusEnum(row.upload_status),
        views_count=row.views_count,
        thumbnail_s3_key=row.thumbnail_s3_key,
        created_at=row.created_at,
    )
