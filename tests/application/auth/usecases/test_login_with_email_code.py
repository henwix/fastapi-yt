from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.usecases import LoginWithEmailCodeUseCase
from tests.factories.commands.auth import LoginWithEmailCodeCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_login_with_email_code_returns_none_if_login_code_task_scheduled(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        command = LoginWithEmailCodeCommandFactory.build(email=channel.email)

        with patch.object(use_case._email_service, 'schedule_send_login_email_code') as email_service_mock:
            result = await use_case.execute(command=command)

        email_service_mock.assert_called_once()
        assert result is None


@pytest.mark.asyncio
async def test_login_with_email_code_returns_none_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeUseCase)

        command = LoginWithEmailCodeCommandFactory.build()

        with patch.object(use_case._email_service, 'schedule_send_login_email_code') as email_service_mock:
            result = await use_case.execute(command=command)

        email_service_mock.assert_not_called()
        assert result is None
