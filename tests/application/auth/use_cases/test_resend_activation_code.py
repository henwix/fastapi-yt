from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.resend_channel_activation import ResendChannelActivationCodeUseCase
from app.domain.auth.exceptions import ChannelAlreadyActivatedError
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.common.repos.kv import IKVRepo
from tests.factories.commands.auth import ResendChannelActivationCodeCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_resend_activation_code_returns_none_if_email_sent(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(ResendChannelActivationCodeUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = ResendChannelActivationCodeCommandFactory.build(current_channel_id=db_channel.id)

        with patch.object(use_case._email_task_queue, 'send_channel_activation_code') as mock_email_task_queue:
            result = await use_case.execute(command=command)

        assert result is None
        mock_email_task_queue.assert_called_once()

        code = await kv_repo.get(f'auth:activation:code:{db_channel.id}')
        assert code is not None
        assert len(code) == 32


@pytest.mark.asyncio
async def test_resend_activation_code_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(ResendChannelActivationCodeUseCase)

        command = ResendChannelActivationCodeCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_resend_activation_code_raises_error_if_channel_already_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(ResendChannelActivationCodeUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        command = ResendChannelActivationCodeCommandFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelAlreadyActivatedError):
            await use_case.execute(command=command)
