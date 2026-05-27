from dataclasses import dataclass
from typing import Any

from sqlalchemy import exists, select

from app.domain.channels.entities import Channel
from app.domain.channels.repository import IChannelRepository
from app.infrastructure.sqlalchemy.database import Database
from app.infrastructure.sqlalchemy.models.channels import ChannelORM


@dataclass
class SAChannelRepository(IChannelRepository):
    db: Database

    async def _check_channel_exists_by_field(self, field: Any, value: Any) -> bool:
        async with self.db.get_read_only_session() as session:
            stmt = select(exists().where(field == value))
            result = await session.execute(stmt)
        return result.scalar_one()

    async def create(self, channel: Channel) -> Channel:
        model = ChannelORM.from_entity(entity=channel)
        async with self.db.get_session() as session:
            session.add(instance=model)
        return model.to_entity()

    async def check_channel_exists_by_slug(self, slug: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.slug, value=slug)

    async def check_channel_exists_by_email(self, email: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.email, value=email)
