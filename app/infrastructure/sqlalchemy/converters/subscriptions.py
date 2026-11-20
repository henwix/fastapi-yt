from sqlalchemy import RowMapping

from app.application.subscriptions.dto import DetailedSubscription
from app.core.configs import settings


def convert_row_to_detailed_subscription_dto(row: RowMapping) -> DetailedSubscription:
    return DetailedSubscription(
        subscription_id=row.id,
        channel_slug=row.slug,
        created_at=row.created_at,
        channel_avatar_url=f'{settings.s3_public_bucket_url}/{row.channel_avatar_key}'
        if row.channel_avatar_key
        else None,
    )
