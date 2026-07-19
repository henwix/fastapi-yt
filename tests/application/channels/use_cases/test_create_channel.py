import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelWithEmailAlreadyExistsError, ChannelWithSlugAlreadyExistsError
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from tests.factories.commands.channels import CreateChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_create_channel_returns_correct_entity_if_created(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateChannelUseCase)
        session = await di.get(AsyncSession)
        pwd_hasher = await di.get(IPasswordHasher)
        command = CreateChannelCommandFactory.build()

        created_channel = await use_case.execute(command=command)

        stmt = select(ChannelORM).where(ChannelORM.id == created_channel.id)
        result = await session.execute(statement=stmt)
        db_channel = result.scalar_one()

        assert isinstance(created_channel, Channel)
        assert created_channel.email == command.email
        assert created_channel.name == command.name
        assert created_channel.slug == command.slug
        assert created_channel.description == command.description
        assert created_channel.country == command.country
        assert pwd_hasher.verify_password_hash(password=command.password, hash=created_channel.password_hash)

        assert db_channel.email == command.email
        assert db_channel.name == command.name
        assert db_channel.slug == command.slug
        assert db_channel.description == command.description
        assert db_channel.country == command.country
        assert pwd_hasher.verify_password_hash(password=command.password, hash=db_channel.password_hash)


@pytest.mark.asyncio
async def test_create_channel_raises_error_if_email_exists(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session)
        command = CreateChannelCommandFactory.build(email=db_channel.email)

        with pytest.raises(ChannelWithEmailAlreadyExistsError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_channel_raises_error_if_slug_exists(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session)
        command = CreateChannelCommandFactory.build(slug=db_channel.slug)

        with pytest.raises(ChannelWithSlugAlreadyExistsError):
            await use_case.execute(command=command)
