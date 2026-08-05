from sqlalchemy import RowMapping

from app.application.video_history.dto import PreviewVideoHistoryDTO
from app.domain.videos.enums import VideoPrivacyStatusEnum


def convert_row_to_preview_video_history_dto(row: RowMapping) -> PreviewVideoHistoryDTO:
    return PreviewVideoHistoryDTO(
        id=row['id'],
        title=row['title'],
        privacy_status=VideoPrivacyStatusEnum(row['privacy_status']),
        created_at=row['created_at'],
        views_count=row['views_count'],
        watched_at=row['watched_at'],
        author_name=row['author_name'],
        author_slug=row['author_slug'],
    )
