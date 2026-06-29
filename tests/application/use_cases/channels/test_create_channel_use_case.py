import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.commands import CreateChannelCommand
from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.channels.entities import Channel
from app.infrastructure.sqlalchemy.models.channels import ChannelORM


@pytest.mark.asyncio
async def test_channel_created(container: AsyncContainer):
    expected_email = 'email@test.com'
    expected_name = 'test_name'
    expected_slug = 'test_slug'
    expected_desc = 'test_desc'
    expected_country = 'test_country'
    expected_password = 'test_password'

    command = CreateChannelCommand(
        email=expected_email,
        name=expected_name,
        slug=expected_slug,
        description=expected_desc,
        country=expected_country,
        password=expected_password,
    )

    async with container() as di:
        session = await di.get(AsyncSession)
        pwd_hasher = await di.get(IPasswordHasher)
        use_case = await di.get(CreateChannelUseCase)

        created_channel = await use_case.execute(command=command)

        stmt = select(ChannelORM).where(ChannelORM.id == created_channel.id)
        result = await session.execute(statement=stmt)
        db_channel = result.scalar_one()

        assert isinstance(created_channel, Channel)
        assert created_channel.email == expected_email
        assert created_channel.name == expected_name
        assert created_channel.slug == expected_slug
        assert created_channel.description == expected_desc
        assert created_channel.country == expected_country
        assert pwd_hasher.verify_password_hash(password=expected_password, hash=created_channel.password_hash)

        assert db_channel.email == expected_email
        assert db_channel.name == expected_name
        assert db_channel.slug == expected_slug
        assert db_channel.description == expected_desc
        assert db_channel.country == expected_country
        assert pwd_hasher.verify_password_hash(password=expected_password, hash=db_channel.password_hash)
