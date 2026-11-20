from sqlalchemy import RowMapping

from app.application.posts.dto import DetailedPost
from app.core.configs import settings


def convert_row_to_detailed_post_dto(row: RowMapping) -> DetailedPost:
    return DetailedPost(
        id=row.id,
        text=row.text,
        created_at=row.created_at,
        channel_name=row.channel_name,
        channel_slug=row.channel_slug,
        channel_avatar_url=f'{settings.s3_public_bucket_url}/{row.channel_avatar_key}'
        if row.channel_avatar_key
        else None,
    )
