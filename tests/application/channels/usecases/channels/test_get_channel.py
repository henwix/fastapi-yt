from datetime import datetime

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.usecases import GetChannelUseCase
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.utils.datetime import get_current_utc_datetime
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.queries.channels import GetChannelQueryFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('deleted_at', [None, get_current_utc_datetime()])
async def test_get_channel_returns_correct_channel_entity(
    mock_container: AsyncContainer,
    deleted_at: datetime | None,
):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, deleted_at=deleted_at)
        query = GetChannelQueryFactory.build(current_channel_id=db_channel.id)

        retrieved_channel = await use_case.execute(query=query)

        assert isinstance(retrieved_channel, Channel)
        assert retrieved_channel.id == db_channel.id
        assert retrieved_channel.email.to_raw() == db_channel.email
        assert retrieved_channel.name.to_raw() == db_channel.name
        assert retrieved_channel.slug.to_raw() == db_channel.slug
        assert retrieved_channel.description == db_channel.description
        assert retrieved_channel.country == db_channel.country
        assert retrieved_channel.password_hash == db_channel.password_hash
        assert retrieved_channel.is_active == db_channel.is_active
        assert retrieved_channel.created_at == db_channel.created_at
        assert retrieved_channel.updated_at == db_channel.updated_at
        if deleted_at is not None:
            assert retrieved_channel.deleted_at.is_deleted
        else:
            assert not retrieved_channel.deleted_at.is_deleted


@pytest.mark.asyncio
async def test_get_channel_returns_correct_channel_entity_if_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        query = GetChannelQueryFactory.build(current_channel_id=db_channel.id)

        retrieved_channel = await use_case.execute(query=query)

        assert isinstance(retrieved_channel, Channel)
        assert retrieved_channel.id == db_channel.id
        assert retrieved_channel.email.to_raw() == db_channel.email
        assert retrieved_channel.name.to_raw() == db_channel.name
        assert retrieved_channel.slug.to_raw() == db_channel.slug
        assert retrieved_channel.description == db_channel.description
        assert retrieved_channel.country == db_channel.country
        assert retrieved_channel.password_hash == db_channel.password_hash
        assert retrieved_channel.is_active == db_channel.is_active
        assert retrieved_channel.created_at == db_channel.created_at
        assert retrieved_channel.updated_at == db_channel.updated_at


@pytest.mark.asyncio
async def test_get_channel_raises_error_if_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        query = GetChannelQueryFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(query=query)
