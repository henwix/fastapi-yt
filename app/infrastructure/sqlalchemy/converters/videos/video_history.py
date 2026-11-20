from sqlalchemy import RowMapping

from app.application.videos.dto import PreviewVideoHistory
from app.core.configs import settings
from app.domain.videos.enums import VideoPrivacyStatusEnum


def convert_row_to_preview_video_history_dto(row: RowMapping) -> PreviewVideoHistory:
    return PreviewVideoHistory(
        id=row.id,
        title=row.title,
        privacy_status=VideoPrivacyStatusEnum(row.privacy_status),
        created_at=row.created_at,
        views_count=row.views_count,
        watched_at=row.watched_at,
        channel_name=row.channel_name,
        channel_slug=row.channel_slug,
        video_thumbnail_url=f'{settings.s3_public_bucket_url}/{row.video_thumbnail_key}'
        if row.video_thumbnail_key
        else None,
    )
