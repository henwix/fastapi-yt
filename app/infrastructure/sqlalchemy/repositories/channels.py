from dataclasses import dataclass
from typing import Any, NoReturn
from uuid import UUID

from sqlalchemy import delete, exists, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelWithEmailAlreadyExistsError, ChannelWithSlugAlreadyExistsError
from app.domain.channels.repositories import IChannelRepository
from app.infrastructure.sqlalchemy.models.channels import ChannelORM


@dataclass
class SAChannelRepository(IChannelRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, channel: Channel) -> NoReturn:
        cause = error.orig.__cause__
        if cause is None:
            raise error

        match cause.constraint_name:
            case 'channels_email_key':
                raise ChannelWithEmailAlreadyExistsError(email=channel.email) from error
            case 'channels_slug_key':
                raise ChannelWithSlugAlreadyExistsError(slug=channel.slug) from error
            case _:
                raise error

    async def _check_channel_exists_by_field(self, field: Any, value: Any) -> bool:
        stmt = select(exists().where(field == value))
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def _get_one_by_query(self, query) -> Channel | None:
        result = await self._session.execute(statement=query)
        channel = result.scalar_one_or_none()
        return channel.to_entity() if channel else None

    async def create(self, channel: Channel) -> Channel:
        model = ChannelORM.from_entity(entity=channel)
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, channel=channel)
        return model.to_entity()

    async def get_by_email(self, email: str) -> Channel | None:
        stmt = select(ChannelORM).where(ChannelORM.email == email)
        return await self._get_one_by_query(query=stmt)

    async def get_by_slug(self, slug: str) -> Channel | None:
        stmt = select(ChannelORM).where(ChannelORM.slug == slug)
        return await self._get_one_by_query(query=stmt)

    async def get_by_id(self, id: UUID) -> Channel | None:
        stmt = select(ChannelORM).where(ChannelORM.id == id)
        return await self._get_one_by_query(query=stmt)

    async def update(self, channel: Channel) -> Channel | None:
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
        try:
            result = await self._session.execute(statement=stmt)
        except IntegrityError as e:
            self._parse_db_error(error=e, channel=channel)

        orm_channel = result.scalar_one_or_none()
        return orm_channel.to_entity() if orm_channel else None

    async def set_password(self, id: UUID, password_hash: str) -> bool:
        stmt = update(ChannelORM).where(ChannelORM.id == id).values(password_hash=password_hash)
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = delete(ChannelORM).where(ChannelORM.id == id)
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0

    async def check_channel_exists_by_slug(self, slug: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.slug, value=slug)

    async def check_channel_exists_by_email(self, email: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.email, value=email)
