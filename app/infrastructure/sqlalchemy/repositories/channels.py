from dataclasses import dataclass
from typing import Any

from sqlalchemy import delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundError
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

    async def try_get_active_by_id(self, id: int) -> Channel:
        stmt = select(ChannelORM).where(ChannelORM.id == id)
        result = await self._session.execute(statement=stmt)
        channel = result.scalar_one_or_none()

        if not channel:
            raise ChannelNotFoundError
        if not channel.is_active:
            raise ChannelNotActiveError
        return channel.to_entity()

    async def update(self, channel: Channel) -> Channel:
        stmt = (
            update(ChannelORM)
            .where(ChannelORM.id == channel.id)
            .values(
                name=channel.name,
                slug=channel.slug,
                description=channel.description,
                country=channel.country,
            )
            .returning(ChannelORM)
        )
        result = await self._session.execute(statement=stmt)
        updated_channel = result.scalar_one_or_none()

        if not updated_channel:
            raise ChannelNotFoundError
        return updated_channel.to_entity()

    async def try_delete_by_id(self, id: int) -> bool:
        stmt = delete(ChannelORM).where(ChannelORM.id == id)
        result = await self._session.execute(statement=stmt)
        if not result.rowcount > 0:
            raise ChannelNotFoundError
        return True
