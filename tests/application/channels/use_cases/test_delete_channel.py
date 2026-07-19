from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.commands import DeleteChannelCommand
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_delete_channel_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=True)
        command = DeleteChannelCommand(current_channel_id=db_channel.id)

        stmt = select(exists().where(ChannelORM.id == db_channel.id))

        is_channel_exists_in_db = await session.execute(statement=stmt)
        assert is_channel_exists_in_db.scalar_one()

        use_case_result = await use_case.execute(command=command)
        assert use_case_result is None

        is_channel_exists_in_db = await session.execute(statement=stmt)
        assert not is_channel_exists_in_db.scalar_one()


@pytest.mark.asyncio
async def test_delete_channel_raises_error_if_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = DeleteChannelCommand(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_raises_error_if_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelUseCase)
        command = DeleteChannelCommand(current_channel_id=uuid7())

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
