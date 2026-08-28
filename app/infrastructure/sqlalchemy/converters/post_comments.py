from sqlalchemy import RowMapping

from app.application.post_comments.dto import DetailedPostComment


def convert_row_to_detailed_post_comment_dto(row: RowMapping) -> DetailedPostComment:
    return DetailedPostComment(
        id=row.id,
        text=row.text,
        reply_level=row.reply_level,
        is_edited=row.is_edited,
        reply_comment_id=row.reply_comment_id,
        created_at=row.created_at,
        author_slug=row.author_slug,
    )
