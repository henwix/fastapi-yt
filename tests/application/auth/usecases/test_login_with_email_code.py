from datetime import datetime
from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.usecases import LoginWithEmailCodeUseCase
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.auth import LoginWithEmailCodeCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('is_channel_active', 'deleted_at'),
    [
        (False, get_current_utc_datetime()),
        (True, None),
    ],
)
async def test_login_with_email_code_returns_none_if_login_code_task_scheduled(
    container: AsyncContainer,
    is_channel_active: bool,
    deleted_at: datetime | None,
):
    async with container() as di:
        use_case = await di.get(LoginWithEmailCodeUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, is_active=is_channel_active, deleted_at=deleted_at)

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
