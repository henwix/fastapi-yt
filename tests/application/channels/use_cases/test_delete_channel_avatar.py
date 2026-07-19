from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.use_cases.delete_channel_avatar import DeleteChannelAvatarUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelAvatarNotFoundError, ChannelNotActiveError, ChannelNotFoundByIdError
from tests.factories.commands.channels import DeleteChannelAvatarCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_delete_channel_avatar_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.png'
        channel = await ChannelORMFactory.create(session=session, is_active=True, avatar_s3_key=expected_avatar_s3_key)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        assert channel.avatar_s3_key == expected_avatar_s3_key

        with patch.object(use_case._task_queue, 'delete_s3_object') as mock_task_queue:
            result = await use_case.execute(command=command)

        mock_task_queue.assert_called_once()
        assert result is None
        assert channel.avatar_s3_key is None


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)

        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=uuid7())

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_avatar_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True, avatar_s3_key=None)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelAvatarNotFoundError):
            await use_case.execute(command=command)
