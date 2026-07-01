from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.queries import GetChannelQuery
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_get_channel_returns_correct_channel_entity(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=True)
        query = GetChannelQuery(current_channel_id=db_channel.id)

        retrieved_channel = await use_case.execute(query=query)

        assert isinstance(retrieved_channel, Channel)
        assert retrieved_channel.id == db_channel.id
        assert retrieved_channel.email == db_channel.email
        assert retrieved_channel.name == db_channel.name
        assert retrieved_channel.slug == db_channel.slug
        assert retrieved_channel.description == db_channel.description
        assert retrieved_channel.country == db_channel.country
        assert retrieved_channel.password_hash == db_channel.password_hash
        assert retrieved_channel.is_active == db_channel.is_active
        assert retrieved_channel.created_at == db_channel.created_at
        assert retrieved_channel.updated_at == db_channel.updated_at


@pytest.mark.asyncio
async def test_get_channel_raises_error_if_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        query = GetChannelQuery(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(query=query)


@pytest.mark.asyncio
async def test_get_channel_raises_error_if_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetChannelUseCase)
        query = GetChannelQuery(current_channel_id=uuid7())

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(query=query)
