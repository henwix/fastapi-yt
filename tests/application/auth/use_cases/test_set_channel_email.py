from unittest.mock import patch

import msgspec
import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.set_channel_email import SetChannelEmailUseCase
from app.domain.auth.exceptions import ChannelEmailAlreadyAssociatedWithThisAcccountError
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
)
from app.domain.common.repos.kv import IKVRepo
from tests.factories.commands.auth import SetChannelEmailCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_set_channel_email_returns_none_if_email_sent(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(SetChannelEmailUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        db_channel = await ChannelORMFactory.create(session=session)
        command = SetChannelEmailCommandFactory.build(current_channel_id=db_channel.id)

        with patch.object(use_case._email_task_queue, 'send_channel_set_email_code') as mock_email_task_queue:
            result = await use_case.execute(command=command)

        assert result is None
        mock_email_task_queue.assert_called_once()

        saved_code_and_channel = await kv_repo.get(f'auth:set_email:code_and_email:{db_channel.id}')
        assert isinstance(saved_code_and_channel, str)

        decoded_saved_code_and_channel: dict[str, str] = msgspec.json.decode(saved_code_and_channel)
        assert len(decoded_saved_code_and_channel['code']) == 32
        assert decoded_saved_code_and_channel['new_email'] == command.new_email


@pytest.mark.asyncio
async def test_set_channel_email_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(SetChannelEmailUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = SetChannelEmailCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_set_channel_email_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(SetChannelEmailUseCase)
        command = SetChannelEmailCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_set_channel_email_raises_error_if_email_already_associated_with_this_channel(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(SetChannelEmailUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        command = SetChannelEmailCommandFactory.build(current_channel_id=db_channel.id, new_email=db_channel.email)

        with pytest.raises(ChannelEmailAlreadyAssociatedWithThisAcccountError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_set_channel_email_raises_error_if_email_already_exists(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(SetChannelEmailUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        second_db_channel = await ChannelORMFactory.create(session=session)
        command = SetChannelEmailCommandFactory.build(
            current_channel_id=db_channel.id,
            new_email=second_db_channel.email,
        )

        with pytest.raises(ChannelWithEmailAlreadyExistsError):
            await use_case.execute(command=command)
