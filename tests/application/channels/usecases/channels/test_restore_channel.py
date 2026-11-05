from datetime import datetime

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.usecases import RestoreChannelUseCase
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelNotDeletedError, ChannelNotFoundByIdError
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
        channel = await ChannelORMFactory.create_deleted(session=session, is_active=is_channel_active)
        command = RestoreChannelCommandFactory.build(current_channel_id=channel.id)

        assert isinstance(channel.deleted_at, datetime)
        assert channel.deletion_status == ChannelDeletionStatusEnum.DELETED.value

        result = await use_case.execute(command=command)

        assert result is None
        assert channel.deleted_at is None
        assert channel.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value


@pytest.mark.asyncio
async def test_restore_channel_raises_error_if_not_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(RestoreChannelUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        command = RestoreChannelCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotDeletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_restore_channel_raises_not_found_error_if_channel_deletion_status_purging(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(RestoreChannelUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        command = RestoreChannelCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
