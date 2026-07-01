from copy import deepcopy

import pytest
from dishka import AsyncContainer
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithSlugAlreadyExistsError,
)
from app.domain.common.constants import Empty
from tests.factories.commands.channels import UpdateChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory

fake = Faker()


@pytest.mark.asyncio
@pytest.mark.parametrize(argnames='expected_slug', argvalues=[fake.slug(), Empty.UNSET])
async def test_update_channel_returns_correct_entity_if_updated(
    container: AsyncContainer,
    expected_slug: str | Empty,
):
    async with container() as di:
        use_case = await di.get(UpdateChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = deepcopy(await ChannelORMFactory.create(session=session, is_active=True))
        command = UpdateChannelCommandFactory.build(current_channel_id=db_channel.id, slug=expected_slug)

        updated_channel = await use_case.execute(command=command)

        assert isinstance(updated_channel, Channel)
        assert updated_channel.id == db_channel.id
        assert updated_channel.email == db_channel.email
        assert updated_channel.password_hash == db_channel.password_hash
        assert updated_channel.is_active == db_channel.is_active
        assert updated_channel.created_at == db_channel.created_at
        assert updated_channel.updated_at > db_channel.updated_at

        assert updated_channel.name == command.name if command.name is not Empty.UNSET else db_channel.name
        assert updated_channel.slug == command.slug if command.slug is not Empty.UNSET else db_channel.slug
        assert (
            updated_channel.description == command.description
            if command.description is not Empty.UNSET
            else db_channel.description
        )
        assert updated_channel.country == command.country if command.country is not Empty.UNSET else db_channel.country


@pytest.mark.asyncio
async def test_update_channel_raises_error_if_slug_exists(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=True)
        command = UpdateChannelCommandFactory.build(current_channel_id=db_channel.id, slug=db_channel.slug)

        with pytest.raises(ChannelWithSlugAlreadyExistsError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_update_channel_raises_error_if_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = UpdateChannelCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_update_channel_raises_error_if_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateChannelUseCase)
        command = UpdateChannelCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
