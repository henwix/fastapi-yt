import secrets
from unittest.mock import patch
from uuid import UUID

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.usecases import ConfirmChannelAvatarUploadUseCase
from app.core.configs import settings
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidContentTypeError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarSizeTooBigError,
    ChannelAvatarSizeTooSmallError,
    ChannelDeletedError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.common.exceptions.s3 import S3ObjectAccessForbiddenError
from app.domain.common.repos.kv import IKVRepo
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.infrastructure.sqlalchemy.models import FileCleanupORM, FileORM
from tests.factories.commands.channels import ConfirmChannelAvatarUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        'expected_content_length',
        'expected_file_format',
    ),
    [
        (314572, 'png'),
        (104857, 'jpg'),
        (943718, 'jpeg'),
        (1048576, 'webp'),
        (1572864, 'png'),
        (2097152, 'jpg'),
        (3145728, 'jpeg'),
        (4194304, 'webp'),
        (5138022, 'png'),
        (5242880, 'jpg'),
    ],
)
async def test_confirm_channel_avatar_upload_returns_none_if_avatar_updated_without_existing_avatar(
    mock_container: AsyncContainer,
    expected_content_length: int,
    expected_file_format: str,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        kv_repo = await di.get(IKVRepo)
        session = await di.get(AsyncSession)

        expected_bucket = settings.s3_public_bucket_name
        base_key = f'{secrets.token_hex(4)}_new_avatar'
        expected_tmp_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/{base_key}.{expected_file_format}'
        expected_new_avatar_key = f'{settings.s3_channel_avatars_key_prefix}/{base_key}.{expected_file_format}'

        channel = await ChannelORMFactory.create(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_tmp_avatar_key
        )

        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{expected_bucket}:{expected_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )

        use_case._s3_service.METADATA_CHANNEL_ID = channel.id
        use_case._s3_service.CONTENT_LENGTH = expected_content_length

        assert channel.avatar_file_id is None

        with (
            patch.object(use_case._s3_service, 'copy_object') as mock_copy_object,
        ):
            result = await use_case.execute(command)

        await session.refresh(instance=channel)

        mock_copy_object.assert_called_once()
        assert result is None
        assert isinstance(channel.avatar_file_id, UUID)

        new_file_stmt = select(FileORM).where(FileORM.id == channel.avatar_file_id)
        tmp_file_cleanup_stmt = select(FileCleanupORM).where(
            FileCleanupORM.key == expected_tmp_avatar_key, FileCleanupORM.bucket == expected_bucket
        )
        db_new_file = (await session.execute(statement=new_file_stmt)).scalar_one()
        db_tmp_file_cleanup = (await session.execute(statement=tmp_file_cleanup_stmt)).scalar_one()

        assert db_new_file.bucket == expected_bucket
        assert db_new_file.key == expected_new_avatar_key

        assert db_tmp_file_cleanup.key == expected_tmp_avatar_key
        assert db_tmp_file_cleanup.bucket == expected_bucket
        assert db_tmp_file_cleanup.status == FileCleanupStatusEnum.PENDING.value
        assert db_tmp_file_cleanup.locked_until is None
        assert db_tmp_file_cleanup.error_code is None
        assert db_tmp_file_cleanup.error_message is None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        'expected_content_length',
        'expected_file_format',
    ),
    [
        (314572, 'png'),
        (104857, 'jpg'),
        (943718, 'jpeg'),
        (1048576, 'webp'),
        (1572864, 'png'),
        (2097152, 'jpg'),
        (3145728, 'jpeg'),
        (4194304, 'webp'),
        (5138022, 'png'),
        (5242880, 'jpg'),
    ],
)
async def test_confirm_channel_avatar_upload_returns_none_if_avatar_updated_with_existing_avatar(
    mock_container: AsyncContainer,
    expected_content_length: int,
    expected_file_format: str,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        kv_repo = await di.get(IKVRepo)
        session = await di.get(AsyncSession)

        expected_bucket = settings.s3_public_bucket_name
        base_key = f'{secrets.token_hex(4)}_new_avatar'
        expected_existing_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/_existing_avatar.{expected_file_format}'
        )
        expected_tmp_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/{base_key}.{expected_file_format}'
        expected_new_avatar_key = f'{settings.s3_channel_avatars_key_prefix}/{base_key}.{expected_file_format}'

        existing_avatar_file = await FileORMFactory.create(
            session=session,
            key=expected_existing_avatar_key,
            bucket=expected_bucket,
        )
        channel = await ChannelORMFactory.create(session=session, avatar_file_id=existing_avatar_file.id)
        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{expected_bucket}:{expected_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_tmp_avatar_key
        )

        use_case._s3_service.METADATA_CHANNEL_ID = channel.id
        use_case._s3_service.CONTENT_LENGTH = expected_content_length

        assert channel.avatar_file_id == existing_avatar_file.id

        with (
            patch.object(use_case._s3_service, 'copy_object') as mock_copy_object,
        ):
            result = await use_case.execute(command)

        await session.refresh(instance=channel)

        mock_copy_object.assert_called_once()
        assert result is None

        assert channel.avatar_file_id != existing_avatar_file.id

        new_file_stmt = select(FileORM).where(FileORM.id == channel.avatar_file_id)
        tmp_file_cleanup_stmt = select(FileCleanupORM).where(
            FileCleanupORM.key == expected_tmp_avatar_key, FileCleanupORM.bucket == expected_bucket
        )
        old_file_cleanup_stmt = select(FileCleanupORM).where(
            FileCleanupORM.key == expected_existing_avatar_key, FileCleanupORM.bucket == expected_bucket
        )
        db_new_file = (await session.execute(statement=new_file_stmt)).scalar_one()
        db_tmp_file_cleanup = (await session.execute(statement=tmp_file_cleanup_stmt)).scalar_one()
        db_old_file_cleanup = (await session.execute(statement=old_file_cleanup_stmt)).scalar_one()

        assert db_new_file.bucket == expected_bucket
        assert db_new_file.key == expected_new_avatar_key

        assert db_tmp_file_cleanup.key == expected_tmp_avatar_key
        assert db_tmp_file_cleanup.bucket == expected_bucket
        assert db_tmp_file_cleanup.status == FileCleanupStatusEnum.PENDING.value
        assert db_tmp_file_cleanup.locked_until is None
        assert db_tmp_file_cleanup.error_code is None
        assert db_tmp_file_cleanup.error_message is None

        assert db_old_file_cleanup.key == expected_existing_avatar_key
        assert db_old_file_cleanup.bucket == expected_bucket
        assert db_old_file_cleanup.status == FileCleanupStatusEnum.PENDING.value
        assert db_old_file_cleanup.locked_until is None
        assert db_old_file_cleanup.error_code is None
        assert db_old_file_cleanup.error_message is None


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_file_format', ['mp4', 'mov', 'gif', 'hjhfsf', 'mkv', 'webm'])
async def test_confirm_channel_avatar_upload_raises_error_if_invalid_invalid_file_format(
    mock_container: AsyncContainer,
    expected_file_format: str,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.{expected_file_format}'
        )

        channel = await ChannelORMFactory.create(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(current_channel_id=channel.id, key=expected_avatar_key)

        with pytest.raises(ChannelAvatarInvalidKeyError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_invalid_key(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'invalid-avatar-prefix/{secrets.token_hex(4)}_new_avatar.png'

        channel = await ChannelORMFactory.create(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(current_channel_id=channel.id, key=expected_avatar_key)

        with pytest.raises(ChannelAvatarInvalidKeyError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)

        expected_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'

        command = ConfirmChannelAvatarUploadCommandFactory.build(key=expected_avatar_key)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_not_active(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = ConfirmChannelAvatarUploadCommandFactory.build(current_channel_id=channel.id, key=expected_avatar_key)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_deleted(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'

        channel = await ChannelORMFactory.create_deleted(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(current_channel_id=channel.id, key=expected_avatar_key)

        with pytest.raises(ChannelDeletedError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_deletion_status_purging(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'

        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(current_channel_id=channel.id, key=expected_avatar_key)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_channel_avatar_already_set(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_old_avatar_filename = 'old_avatar.png'

        avatar_file = await FileORMFactory.create(
            session=session,
            key=f'{settings.s3_channel_avatars_key_prefix}/{expected_old_avatar_filename}',
            bucket=settings.s3_public_bucket_name,
        )
        channel = await ChannelORMFactory.create(session=session, avatar_file_id=avatar_file.id)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id,
            key=f'{settings.s3_tmp_channel_avatars_key_prefix}/{expected_old_avatar_filename}',
        )

        with pytest.raises(ChannelAvatarAlreadySetError):
            await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_file_key_not_found_in_kv(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)

        expected_tmp_avatar_key = f'{settings.s3_tmp_channel_avatars_key_prefix}/new_file.png'

        channel = await ChannelORMFactory.create(session=session)
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_tmp_avatar_key
        )

        with pytest.raises(ChannelAvatarInvalidKeyError) as e:
            await use_case.execute(command)

        assert e.value.key == command.key
        assert e.value.error_detail == 'upload_url_expired_or_deleted'


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_s3_object_access_forbidden(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        expected_new_tmp_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        )

        channel = await ChannelORMFactory.create(session=session)
        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{settings.s3_public_bucket_name}:{expected_new_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_tmp_avatar_key
        )

        with pytest.raises(S3ObjectAccessForbiddenError):
            await use_case.execute(command)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_content_type', ['image/gif', 'video/mp4', 'video/webm'])
async def test_confirm_channel_avatar_upload_raises_error_if_s3_object_invalid_metadata_content_type(
    mock_container: AsyncContainer,
    expected_content_type: str,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        expected_new_tmp_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        )

        channel = await ChannelORMFactory.create(session=session)
        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{settings.s3_public_bucket_name}:{expected_new_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_tmp_avatar_key
        )

        use_case._s3_service.METADATA_CHANNEL_ID = channel.id
        use_case._s3_service.CONTENT_TYPE = expected_content_type

        file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.key == command.key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )
        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert not db_file_cleanup_exists

        with pytest.raises(ChannelAvatarInvalidContentTypeError) as e:
            await use_case.execute(command)

        assert e.value.metadata_content_type == expected_content_type
        assert e.value.actual_content_type == 'image/png'

        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert db_file_cleanup_exists


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_content_type', ['image/gif', 'video/mp4', 'video/webm'])
async def test_confirm_channel_avatar_upload_raises_error_if_s3_object_invalid_content_type(
    mock_container: AsyncContainer,
    expected_content_type: str,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        expected_new_tmp_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        )

        channel = await ChannelORMFactory.create(session=session)
        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{settings.s3_public_bucket_name}:{expected_new_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_tmp_avatar_key
        )

        use_case._s3_service.METADATA_CHANNEL_ID = channel.id
        use_case._file_type_detector.FILE_TYPE = expected_content_type

        file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.key == command.key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )
        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert not db_file_cleanup_exists

        with pytest.raises(ChannelAvatarInvalidContentTypeError) as e:
            await use_case.execute(command)

        assert e.value.metadata_content_type == 'image/png'
        assert e.value.actual_content_type == expected_content_type

        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert db_file_cleanup_exists


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected_content_length',
    [
        1024 * 1024 * 6,
        1024 * 1024 * 7,
        1024 * 1024 * 9,
        1024 * 1024 * 21,
        1024 * 1024 * 35,
        1024 * 1024 * 125,
        1024 * 1024 * 250,
        1024 * 1024 * 333,
        1024 * 1024 * 452,
    ],
)
async def test_confirm_channel_avatar_upload_raises_error_if_avatar_file_size_too_big(
    mock_container: AsyncContainer,
    expected_content_length: str,
):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        expected_new_tmp_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        )

        channel = await ChannelORMFactory.create(session=session)
        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{settings.s3_public_bucket_name}:{expected_new_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_tmp_avatar_key
        )

        use_case._s3_service.METADATA_CHANNEL_ID = channel.id
        use_case._s3_service.CONTENT_LENGTH = expected_content_length

        file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.key == command.key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )
        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert not db_file_cleanup_exists

        with pytest.raises(ChannelAvatarSizeTooBigError) as e:
            await use_case.execute(command)

        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert db_file_cleanup_exists

        assert e.value.key == command.key
        assert e.value.bucket == settings.s3_public_bucket_name
        assert e.value.file_size == expected_content_length


@pytest.mark.asyncio
async def test_confirm_channel_avatar_upload_raises_error_if_avatar_file_size_too_small(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(ConfirmChannelAvatarUploadUseCase)
        session = await di.get(AsyncSession)
        kv_repo = await di.get(IKVRepo)

        expected_new_tmp_avatar_key = (
            f'{settings.s3_tmp_channel_avatars_key_prefix}/{secrets.token_hex(4)}_new_avatar.png'
        )

        channel = await ChannelORMFactory.create(session=session)
        await kv_repo.set(
            key=f'set_channel_avatar_url:{channel.id}:{settings.s3_public_bucket_name}:{expected_new_tmp_avatar_key}',
            value='',
            ttl_seconds=120,
        )
        command = ConfirmChannelAvatarUploadCommandFactory.build(
            current_channel_id=channel.id, key=expected_new_tmp_avatar_key
        )

        use_case._s3_service.METADATA_CHANNEL_ID = channel.id
        use_case._s3_service.CONTENT_LENGTH = 0

        file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.key == command.key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )
        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert not db_file_cleanup_exists

        with pytest.raises(ChannelAvatarSizeTooSmallError) as e:
            await use_case.execute(command)

        db_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()
        assert db_file_cleanup_exists

        assert e.value.key == command.key
        assert e.value.bucket == settings.s3_public_bucket_name
        assert e.value.file_size == 0
