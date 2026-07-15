from sqlalchemy import RowMapping

from app.application.videos.dto import DetailedVideoDTO
from app.domain.videos.enums import VideoPrivacyStatusEnum


def convert_video_row_to_detailed_dto(row: RowMapping) -> DetailedVideoDTO:
    return DetailedVideoDTO(
        id=row['id'],
        title=row['title'],
        description=row['description'],
        privacy_status=VideoPrivacyStatusEnum(row['privacy_status']),
        s3_key=row['s3_key'],
        is_reported=row['is_reported'],
        created_at=row['created_at'],
        channel_id=row['channel_id'],
        channel_name=row['channel_name'],
        channel_slug=row['channel_slug'],
    )
