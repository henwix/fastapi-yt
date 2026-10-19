from datetime import datetime

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.usecases import DeleteChannelUseCase
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from tests.factories.commands.channels import DeleteChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_delete_channel_returns_none_if_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session)
        command = DeleteChannelCommandFactory.build(current_channel_id=db_channel.id)

        assert db_channel.deleted_at is None
        assert db_channel.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value

        use_case_result = await use_case.execute(command=command)
        assert use_case_result is None

        assert isinstance(db_channel.deleted_at, datetime)
        assert db_channel.deletion_status == ChannelDeletionStatusEnum.DELETED.value


@pytest.mark.asyncio
async def test_delete_channel_raises_error_if_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = DeleteChannelCommandFactory.build(current_channel_id=channel.id)

        assert channel.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)

        await session.refresh(instance=channel)
        assert channel.deleted_at is None
        assert channel.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value


@pytest.mark.asyncio
async def test_delete_channel_raises_error_if_channel_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create_deleted(session=session)
        command = DeleteChannelCommandFactory.build(current_channel_id=db_channel.id)
        assert isinstance(db_channel.deleted_at, datetime)
        assert db_channel.deletion_status == ChannelDeletionStatusEnum.DELETED.value

        with pytest.raises(ChannelDeletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_raises_error_if_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        command = DeleteChannelCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
