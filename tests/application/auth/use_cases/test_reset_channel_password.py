from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.reset_channel_password import ResetChannelPasswordUseCase
from app.domain.common.repos.kv import IKVRepo
from tests.factories.commands.auth import ResetChannelPasswordCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('is_channel_active', [True, False])
async def test_reset_channel_password_returns_none_if_email_sent(container: AsyncContainer, is_channel_active: bool):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        db_channel = await ChannelORMFactory.create(session=session, is_active=is_channel_active)

        command = ResetChannelPasswordCommandFactory.build(email=db_channel.email)

        with patch.object(use_case._email_task_queue, 'send_channel_reset_password_code') as mock_email_task_queue:
            result = await use_case.execute(command=command)

        assert result is None
        mock_email_task_queue.assert_called_once()

        code = await kv_repo.get(f'auth:reset_password:code:{db_channel.id}')
        assert code is not None
        assert len(code) == 32


@pytest.mark.asyncio
@pytest.mark.parametrize('is_channel_active', [True, False])
async def test_reset_channel_password_returns_none_if_channel_not_found_by_email(
    container: AsyncContainer, is_channel_active: bool
):
    async with container() as di:
        use_case = await di.get(ResetChannelPasswordUseCase)

        command = ResetChannelPasswordCommandFactory.build()

        with (
            patch.object(use_case._email_task_queue, 'send_channel_reset_password_code') as mock_email_task_queue,
            patch.object(use_case._auth_service, 'create_reset_password_code') as mock_auth_service_create_code,
            patch.object(use_case._auth_service, 'build_reset_password_confirm_url') as mock_auth_service_password_url,
        ):
            result = await use_case.execute(command=command)

        assert result is None
        mock_email_task_queue.assert_not_called()
        mock_auth_service_create_code.assert_not_called()
        mock_auth_service_password_url.assert_not_called()
