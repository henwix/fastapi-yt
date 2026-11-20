from sqlalchemy import RowMapping

from app.application.posts.dto import DetailedPostComment
from app.core.configs import settings


def convert_row_to_detailed_post_comment_dto(row: RowMapping) -> DetailedPostComment:
    return DetailedPostComment(
        id=row.id,
        text=row.text,
        reply_level=row.reply_level,
        is_edited=row.is_edited,
        reply_comment_id=row.reply_comment_id,
        created_at=row.created_at,
        channel_slug=row.channel_slug,
        channel_avatar_url=f'{settings.s3_public_bucket_url}/{row.channel_avatar_key}'
        if row.channel_avatar_key
        else None,
    )
