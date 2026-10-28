from datetime import datetime

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.dto import DetailedChannel
from app.application.channels.usecases import GetChannelUseCase
from app.core.configs import settings
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelNotFoundByIdError
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.queries.channels import GetChannelQueryFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('is_deleted', 'has_avatar'),
    [
        (False, True),
        (True, False),
    ],
)
async def test_get_channel_returns_correct_channel_dto(
    mock_container: AsyncContainer,
    is_deleted: bool,
    has_avatar: bool,
):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        avatar_file = None
        if has_avatar:
            avatar_file = await FileORMFactory.create(
                session=session,
                key=f'{settings.s3_channel_avatars_key_prefix}/test_avatar.png',
            )
        if is_deleted:
            db_channel = await ChannelORMFactory.create_deleted(
                session=session, avatar_file_id=avatar_file.id if avatar_file else None
            )
        else:
            db_channel = await ChannelORMFactory.create(
                session=session, avatar_file_id=avatar_file.id if avatar_file else None
            )
        query = GetChannelQueryFactory.build(current_channel_id=db_channel.id)

        retrieved_channel = await use_case.execute(query=query)

        assert isinstance(retrieved_channel, DetailedChannel)
        assert retrieved_channel.id == db_channel.id
        assert retrieved_channel.email == db_channel.email
        assert retrieved_channel.name == db_channel.name
        assert retrieved_channel.slug == db_channel.slug
        assert retrieved_channel.description == db_channel.description
        assert retrieved_channel.country == db_channel.country
        assert retrieved_channel.is_active == db_channel.is_active
        assert retrieved_channel.created_at == db_channel.created_at
        assert retrieved_channel.updated_at == db_channel.updated_at
        if has_avatar:
            assert retrieved_channel.avatar_url == f'{settings.s3_public_bucket_url}/{avatar_file.key}'
        else:
            assert retrieved_channel.avatar_url is None
        if is_deleted:
            assert retrieved_channel.deletion_status == ChannelDeletionStatusEnum.DELETED
            assert isinstance(retrieved_channel.deleted_at, datetime)
        else:
            assert retrieved_channel.deletion_status == ChannelDeletionStatusEnum.ACTIVE
            assert retrieved_channel.deleted_at is None


@pytest.mark.asyncio
async def test_get_channel_returns_correct_channel_dto_if_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        query = GetChannelQueryFactory.build(current_channel_id=db_channel.id)

        retrieved_channel = await use_case.execute(query=query)

        assert isinstance(retrieved_channel, DetailedChannel)
        assert retrieved_channel.id == db_channel.id
        assert retrieved_channel.email == db_channel.email
        assert retrieved_channel.name == db_channel.name
        assert retrieved_channel.slug == db_channel.slug
        assert retrieved_channel.description == db_channel.description
        assert retrieved_channel.country == db_channel.country
        assert retrieved_channel.is_active == db_channel.is_active
        assert retrieved_channel.created_at == db_channel.created_at
        assert retrieved_channel.updated_at == db_channel.updated_at
        assert retrieved_channel.avatar_url is None


@pytest.mark.asyncio
async def test_get_channel_raises_error_if_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        query = GetChannelQueryFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(query=query)


@pytest.mark.asyncio
async def test_get_channel_raises_error_if_not_found_with_deletion_status_purging(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GetChannelUseCase)
        session = await di.get(AsyncSession)
        db_channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        query = GetChannelQueryFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(query=query)
