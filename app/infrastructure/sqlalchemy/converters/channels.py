from sqlalchemy import RowMapping

from app.application.channels.dto import ChannelAboutInfoDTO


def convert_row_to_channel_about_info_dto(row: RowMapping) -> ChannelAboutInfoDTO:
    return ChannelAboutInfoDTO(
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
