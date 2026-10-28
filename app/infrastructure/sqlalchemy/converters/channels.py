from sqlalchemy import RowMapping

from app.application.channels.dto import ChannelAboutInfo, DetailedChannel
from app.core.configs import settings
from app.domain.channels.enums import ChannelDeletionStatusEnum


def convert_row_to_channel_about_info_dto(row: RowMapping) -> ChannelAboutInfo:
    return ChannelAboutInfo(
        id=row.id,
        name=row.name,
        slug=row.slug,
        description=row.description,
        country=row.country,
        created_at=row.created_at,
        subscribers_count=row.subscribers_count,
        videos_count=row.videos_count,
        views_count=row.views_count,
    )


def convert_row_to_channel_detailed_dto(row: RowMapping) -> DetailedChannel:
    return DetailedChannel(
        id=row.id,
        name=row.name,
        email=row.email,
        slug=row.slug,
        description=row.description,
        country=row.country,
        created_at=row.created_at,
        updated_at=row.updated_at,
        is_active=row.is_active,
        deletion_status=ChannelDeletionStatusEnum(row.deletion_status),
        deleted_at=row.deleted_at,
        avatar_url=f'{settings.s3_public_bucket_url}/{row.avatar_key}' if row.avatar_key is not None else None,
    )
