from typing import Any, NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, exists, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.entities import Channel
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelEmailAlreadyExistsError, ChannelSlugAlreadyExistsError
from app.domain.channels.repos import IChannelRepo
from app.infrastructure.sqlalchemy.models import ChannelORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo
from app.utils.datetime import get_current_utc_datetime


class ChannelRepo(SQLAlchemyRepo, IChannelRepo):
    def _parse_db_error(self, error: DBAPIError, channel: Channel) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'channels_email_key':
                raise ChannelEmailAlreadyExistsError(channel_email=channel.email.to_raw()) from error
            case 'channels_slug_key':
                raise ChannelSlugAlreadyExistsError(channel_slug=channel.slug.to_raw()) from error
            case _:
                raise

    async def _check_channel_exists_by_field(self, field: Any, value: Any) -> bool:
        stmt = select(exists().where(field == value))
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(stmt)
        return result.scalar_one()

    async def _get_one_by_query(self, query) -> Channel | None:
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=query)
        channel = result.scalar_one_or_none()
        return channel.to_entity() if channel else None

    async def create(self, channel: Channel) -> Channel:
        model = ChannelORM.from_entity(entity=channel)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, channel=channel)
        return model.to_entity()

    async def get_by_email(self, email: str) -> Channel | None:
        stmt = select(ChannelORM).where(
            ChannelORM.email == email,
            ChannelORM.deletion_status != ChannelDeletionStatusEnum.PURGING.value,
        )
        return await self._get_one_by_query(query=stmt)

    async def get_existing_by_slug(self, slug: str) -> Channel | None:
        stmt = select(ChannelORM).where(
            ChannelORM.slug == slug,
            ChannelORM.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value,
        )
        return await self._get_one_by_query(query=stmt)

    async def get_by_id(self, id: UUID) -> Channel | None:
        stmt = select(ChannelORM).where(
            ChannelORM.id == id,
            ChannelORM.deletion_status != ChannelDeletionStatusEnum.PURGING.value,
        )
        return await self._get_one_by_query(query=stmt)

    async def update(self, channel: Channel) -> Channel | None:
        stmt = (
            update(ChannelORM)
            .where(ChannelORM.id == channel.id)
            .values(
                email=channel.email.to_raw(),
                name=channel.name.to_raw(),
                slug=channel.slug.to_raw(),
                description=channel.description,
                country=channel.country,
                avatar_s3_key=channel.avatar_s3_key,
            )
            .returning(ChannelORM)
        )
        async with self._db.get_session(commit=True) as session:
            try:
                result = await session.execute(statement=stmt)
            except IntegrityError as e:
                self._parse_db_error(error=e, channel=channel)

        orm_channel = result.scalar_one_or_none()
        return orm_channel.to_entity() if orm_channel else None

    async def restore(self, id: UUID) -> bool:
        stmt = (
            update(ChannelORM)
            .values(
                deletion_status=ChannelDeletionStatusEnum.ACTIVE.value,
                deleted_at=None,
            )
            .where(
                ChannelORM.id == id,
                ChannelORM.deletion_status == ChannelDeletionStatusEnum.DELETED.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = (
            update(ChannelORM)
            .values(
                deletion_status=ChannelDeletionStatusEnum.DELETED.value,
                deleted_at=get_current_utc_datetime(),
            )
            .where(
                ChannelORM.id == id,
                ChannelORM.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def activate(self, id: UUID) -> bool:
        stmt = (
            update(ChannelORM)
            .where(
                ChannelORM.id == id,
                ChannelORM.is_active.is_(False),
            )
            .values(is_active=True)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def set_password(self, id: UUID, password_hash: str) -> bool:
        stmt = update(ChannelORM).where(ChannelORM.id == id).values(password_hash=password_hash)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0

    async def check_channel_exists_by_slug(self, slug: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.slug, value=slug)

    async def check_channel_exists_by_email(self, email: str) -> bool:
        return await self._check_channel_exists_by_field(field=ChannelORM.email, value=email)
