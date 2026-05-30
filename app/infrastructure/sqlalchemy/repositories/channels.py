from dataclasses import dataclass
from typing import Any

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.entities import Channel
from app.domain.channels.repository import IChannelRepository
from app.infrastructure.sqlalchemy.models.channels import ChannelORM


@dataclass
class SAChannelRepository(IChannelRepository):
    _session: AsyncSession

    async def _check_channel_exists_by_field(self, field: Any, value: Any) -> bool:
        stmt = select(exists().where(field == value))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def create(self, channel: Channel) -> Channel:
        model = ChannelORM.from_entity(entity=channel)
        self._session.add(instance=model)
        await self._session.flush()
        return model.to_entity()

    async def check_channel_exists_by_slug(self, slug: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.slug, value=slug)

    async def check_channel_exists_by_email(self, email: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.email, value=email)

    async def get_by_email(self, email: str) -> Channel | None:
        stmt = select(ChannelORM).where(ChannelORM.email == email)
        result = await self._session.execute(statement=stmt)
        channel = result.scalar_one_or_none()
        return channel.to_entity() if channel else None
