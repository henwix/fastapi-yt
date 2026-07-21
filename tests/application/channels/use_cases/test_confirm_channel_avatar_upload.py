from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.use_cases.confirm_channel_avatar_upload import ConfirmChannelAvatarUploadUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidFileContentTypeError,
    ChannelAvatarInvalidFileFormatError,
    ChannelAvatarInvalidKeyError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.common.exceptions import S3ObjectAccessForbiddenError
from tests.factories.commands.channels import ConfirmChannelAvatarUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_file_format', ['png', 'jpg', 'jpeg'])
async def test_confirm_channel_avatar_upload_returns_none_if_avatar_updated_without_existing_avatar(
    container: AsyncContainer,
    expected_file_format: str,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.{expected_file_format}'

        channel = await ChannelORMFactory.create(session=session, avatar_s3_key=None)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_avatar_s3_key
        )

        use_case._s3_provider.METADATA_CHANNEL_ID = channel.id

        assert channel.avatar_s3_key is None

        result = await use_case.execute(command)

        assert result is None
        assert channel.avatar_s3_key == expected_avatar_s3_key


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_returns_none_if_avatar_updated_with_existing_avatar(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_old_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/old_avatar.png'
        expected_new_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.png'

        channel = await ChannelORMFactory.create(
            session=session,
            avatar_s3_key=expected_old_avatar_s3_key,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_avatar_s3_key
        )

        use_case._s3_provider.METADATA_CHANNEL_ID = channel.id

        assert channel.avatar_s3_key == expected_old_avatar_s3_key

        with patch.object(use_case._task_queue, 'delete_s3_object') as mock_task_queue:
            result = await use_case.execute(command)
        mock_task_queue.assert_called_once()

        assert result is None
        assert channel.avatar_s3_key == expected_new_avatar_s3_key


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_file_format', ['mp4', 'mov', 'gif', 'hjhfsf', 'mkv', 'webm'])
async def test_confirm_channel_avatar_upload_raises_error_if_invalid_invalid_file_format(
    container: AsyncContainer,
    expected_file_format: str,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.{expected_file_format}'

        channel = await ChannelORMFactory.create(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_avatar_s3_key
        )

        with pytest.raises(ChannelAvatarInvalidFileFormatError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_invalid_key(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_s3_key = 'invalid-avatar-prefix/new_avatar.png'

        channel = await ChannelORMFactory.create(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_avatar_s3_key
        )

        with pytest.raises(ChannelAvatarInvalidKeyError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)

        expected_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.png'

        command = ConfirmChannelAvatarUploadCommandFactory.build(key=expected_avatar_s3_key)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_not_active(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.png'

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_avatar_s3_key
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_avatar_already_set(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_old_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/old_avatar.png'

        channel = await ChannelORMFactory.create(session=session, avatar_s3_key=expected_old_avatar_s3_key)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_old_avatar_s3_key
        )

        with pytest.raises(ChannelAvatarAlreadySetError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_s3_object_access_forbidden(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_new_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.png'

        channel = await ChannelORMFactory.create(session=session, avatar_s3_key=None)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_avatar_s3_key
        )

        with pytest.raises(S3ObjectAccessForbiddenError):
            await use_case.execute(command)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_content_type', ['image/gif', 'video/mp4', 'video/webm'])
async def test_confirm_channel_avatar_upload_raises_error_if_s3_object_invalid_content_type(
    container: AsyncContainer,
    expected_content_type: str,
):
    async with container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_new_avatar_s3_key = f'{settings.s3_avatars_key_prefix}/new_avatar.png'

        channel = await ChannelORMFactory.create(session=session, avatar_s3_key=None)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_avatar_s3_key
        )

        use_case._s3_provider.METADATA_CHANNEL_ID = channel.id
        use_case._s3_provider.CONTENT_TYPE = expected_content_type

        with patch.object(use_case._task_queue, 'delete_s3_object') as mock_task_queue:
            with pytest.raises(ChannelAvatarInvalidFileContentTypeError):
                await use_case.execute(command)
        mock_task_queue.assert_called_once()
