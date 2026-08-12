import sqlalchemy as sa
from sqlalchemy import select

from app.application.channels.dto import ChannelAboutInfoDTO
from app.application.channels.interfaces.reader import IChannelReader
from app.domain.channels.exceptions import ChannelNotFoundBySlugError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.infrastructure.sqlalchemy.converters.channels import convert_row_to_channel_about_info_dto
from app.infrastructure.sqlalchemy.models.channels import ChannelORM, SubscriptionORM
from app.infrastructure.sqlalchemy.models.videos import VideoORM
from app.infrastructure.sqlalchemy.readers.base import SAReader


class SAChannelReader(SAReader, IChannelReader):
    async def try_get_about_info(self, slug: str) -> ChannelAboutInfoDTO:
        subscribers_count_subquery = (
            select(sa.func.count(SubscriptionORM.subscribed_to_id))
            .where(SubscriptionORM.subscribed_to_id == ChannelORM.id)
            .correlate(ChannelORM)
            .scalar_subquery()
        )
        videos_subquery = (
            select(
                VideoORM.channel_id,
                sa.func.count(VideoORM.id).label('videos_count'),
                sa.func.sum(VideoORM.views_count).label('views_count'),
            )
            .where(
                VideoORM.upload_status == VideoUploadStatusEnum.COMPLETED.value,
                VideoORM.privacy_status == VideoPrivacyStatusEnum.PUBLIC.value,
            )
            .group_by(VideoORM.channel_id)
            .subquery()
        )
        stmt = (
            select(
                ChannelORM.id,
                ChannelORM.name,
                ChannelORM.slug,
                ChannelORM.description,
                ChannelORM.country,
                ChannelORM.created_at,
                subscribers_count_subquery.label('subscribers_count'),
                sa.func.coalesce(videos_subquery.c.videos_count, 0).label('videos_count'),
                sa.func.coalesce(videos_subquery.c.views_count, 0).label('views_count'),
            )
            .outerjoin(videos_subquery, videos_subquery.c.channel_id == ChannelORM.id)
            .where(ChannelORM.slug == slug)
        )
        result = await self._session.execute(statement=stmt)
        row = result.mappings().one_or_none()

        if row is None:
            raise ChannelNotFoundBySlugError(channel_slug=slug)
        return convert_row_to_channel_about_info_dto(row=row)
