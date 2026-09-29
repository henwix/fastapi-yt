from datetime import datetime

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.usecases import RestoreChannelUseCase
from app.domain.channels.exceptions import ChannelNotDeletedError
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.channels import RestoreChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('is_channel_active', [False, True])
async def test_restore_channel_returns_none_if_restored(
    container: AsyncContainer,
    is_channel_active: bool,
):
    async with container() as di:
        use_case = await di.get(RestoreChannelUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(
            session=session, is_active=is_channel_active, deleted_at=get_current_utc_datetime()
        )
        command = RestoreChannelCommandFactory.build(current_channel_id=channel.id)

        assert isinstance(channel.deleted_at, datetime)

        result = await use_case.execute(command=command)

        assert result is None
        assert channel.deleted_at is None


@pytest.mark.asyncio
async def test_restore_channel_raises_error_if_not_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(RestoreChannelUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        command = RestoreChannelCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotDeletedError):
            await use_case.execute(command=command)
