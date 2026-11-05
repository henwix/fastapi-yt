import secrets
from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.usecases import DeleteChannelAvatarUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import (
    ChannelAvatarNotFoundError,
    ChannelDeletedError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.infrastructure.sqlalchemy.models import FileCleanupORM, FileORM
from tests.factories.commands.channels import DeleteChannelAvatarCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory


@pytest.mark.asyncio
async def test_delete_channel_avatar_returns_none_if_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'{settings.s3_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        bucket_name = settings.s3_public_bucket_name
        avatar_file = await FileORMFactory.create(
            session=session,
            key=expected_avatar_key,
            bucket=bucket_name,
        )
        channel = await ChannelORMFactory.create(session=session, avatar_file_id=avatar_file.id)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        avatar_file_exists_stmt = select(
            exists().where(
                FileORM.key == expected_avatar_key,
                FileORM.bucket == bucket_name,
            )
        )
        avatar_cleanup_stmt = select(FileCleanupORM).where(
            FileCleanupORM.key == expected_avatar_key,
            FileCleanupORM.bucket == bucket_name,
        )

        assert channel.avatar_file_id == avatar_file.id
        assert (await session.execute(statement=avatar_file_exists_stmt)).scalar_one()
        assert (await session.execute(statement=avatar_cleanup_stmt)).scalar_one_or_none() is None

        result = await use_case.execute(command=command)

        avatar_cleanup = (await session.execute(statement=avatar_cleanup_stmt)).scalar_one()

        assert not (await session.execute(statement=avatar_file_exists_stmt)).scalar_one()

        await session.refresh(instance=channel)

        assert result is None
        assert channel.avatar_file_id is None

        assert avatar_cleanup.bucket == bucket_name
        assert avatar_cleanup.key == expected_avatar_key
        assert avatar_cleanup.error_code is None
        assert avatar_cleanup.error_message is None
        assert avatar_cleanup.status == FileCleanupStatusEnum.PENDING.value
        assert avatar_cleanup.locked_until is None


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)

        command = DeleteChannelAvatarCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_avatar_raises_error_if_channel_avatar_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelAvatarNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_channel_avatar_reises_error_if_avatar_file_not_found_in_db(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'{settings.s3_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        bucket_name = settings.s3_public_bucket_name
        avatar_file = await FileORMFactory.create(
            session=session,
            key=expected_avatar_key,
            bucket=bucket_name,
        )
        channel = await ChannelORMFactory.create(session=session, avatar_file_id=avatar_file.id)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        with (  # noqa: PT012
            pytest.raises(ChannelAvatarNotFoundError) as e,
            patch.object(use_case._file_service, 'get_by_id') as file_service_mock,
        ):
            file_service_mock.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=channel)
        await session.refresh(instance=avatar_file)

        file_service_mock.assert_called_once_with(id=avatar_file.id)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_delete_channel_avatar_reises_error_if_avatar_file_not_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(DeleteChannelAvatarUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'{settings.s3_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        bucket_name = settings.s3_public_bucket_name
        avatar_file = await FileORMFactory.create(
            session=session,
            key=expected_avatar_key,
            bucket=bucket_name,
        )
        channel = await ChannelORMFactory.create(session=session, avatar_file_id=avatar_file.id)
        command = DeleteChannelAvatarCommandFactory.build(current_channel_id=channel.id)

        avatar_file_exists_stmt = select(
            exists().where(
                FileORM.key == expected_avatar_key,
                FileORM.bucket == bucket_name,
            )
        )
        avatar_cleanup_stmt = select(FileCleanupORM).where(
            FileCleanupORM.key == expected_avatar_key,
            FileCleanupORM.bucket == bucket_name,
        )

        with (  # noqa: PT012
            pytest.raises(ChannelAvatarNotFoundError) as e,
            patch.object(use_case._file_service, 'delete_by_id') as file_service_mock,
        ):
            file_service_mock.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=channel)
        await session.refresh(instance=avatar_file)

        file_service_mock.assert_called_once_with(id=avatar_file.id)

        assert e.value.channel_id == channel.id

        assert (await session.execute(statement=avatar_file_exists_stmt)).scalar_one()
        assert (await session.execute(statement=avatar_cleanup_stmt)).scalar_one_or_none() is None
