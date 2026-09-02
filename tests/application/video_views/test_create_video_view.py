from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.video_views.use_cases.create_video_view import CreateVideoViewUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_views.exceptions import VideoViewsLimitReached
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.infrastructure.sqlalchemy.models.videos import VideoViewORM
from app.utils.datetime import get_current_utc_date
from app.utils.videos import generate_video_id
from tests.factories.commands.video_views import CreateVideoViewCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VIDEO_VIEWS_LIMIT_PER_DAY, VideoORMFactory, VideoViewORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('privacy_status', [VideoPrivacyStatusEnum.PUBLIC.value, VideoPrivacyStatusEnum.UNLISTED.value])
async def test_create_video_view_returns_none_if_created_if_video_public_or_unlisted_and_channel_authenticated(
    mock_container: AsyncContainer,
    privacy_status: str,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=privacy_status,
        )
        old_views_count = video.views_count

        command = CreateVideoViewCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        result = await use_case.execute(command=command)
        stmt = select(
            exists().where(
                VideoViewORM.video_id == video.id,
                VideoViewORM.channel_id == channel.id,
                VideoViewORM.anonymous_id.is_(None),
                VideoViewORM.views_count == 1,
                VideoViewORM.created_at == get_current_utc_date(),
            )
        )
        sql_result_view_exists = await session.execute(statement=stmt)

        assert result is None
        assert video.views_count == old_views_count + 1
        assert sql_result_view_exists.scalar_one()


@pytest.mark.asyncio
@pytest.mark.parametrize('privacy_status', [VideoPrivacyStatusEnum.PUBLIC.value, VideoPrivacyStatusEnum.UNLISTED.value])
async def test_create_video_view_returns_none_if_created_if_video_public_or_unlisted_and_channel_not_authenticated(
    mock_container: AsyncContainer,
    privacy_status: str,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=privacy_status,
        )
        old_views_count = video.views_count

        command = CreateVideoViewCommandFactory.build(current_channel_id=None, video_id=video.id)

        result = await use_case.execute(command=command)
        stmt = select(
            exists().where(
                VideoViewORM.video_id == video.id,
                VideoViewORM.channel_id.is_(None),
                VideoViewORM.anonymous_id == command.anonymous_id,
                VideoViewORM.views_count == 1,
                VideoViewORM.created_at == get_current_utc_date(),
            )
        )
        sql_result_view_exists = await session.execute(statement=stmt)

        assert result is None
        assert video.views_count == old_views_count + 1
        assert sql_result_view_exists.scalar_one()


@pytest.mark.asyncio
async def test_create_video_view_returns_none_if_created_if_video_private_and_channel_author(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
        )
        old_views_count = video.views_count

        command = CreateVideoViewCommandFactory.build(current_channel_id=channel_video_author.id, video_id=video.id)

        result = await use_case.execute(command=command)
        stmt = select(
            exists().where(
                VideoViewORM.video_id == video.id,
                VideoViewORM.channel_id == channel_video_author.id,
                VideoViewORM.anonymous_id.is_(None),
                VideoViewORM.views_count == 1,
                VideoViewORM.created_at == get_current_utc_date(),
            )
        )
        sql_result_view_exists = await session.execute(statement=stmt)

        assert result is None
        assert video.views_count == old_views_count + 1
        assert sql_result_view_exists.scalar_one()


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_video_private_and_channel_not_author(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
        )
        old_views_count = video.views_count

        command = CreateVideoViewCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)

        stmt = select(
            exists().where(
                VideoViewORM.video_id == video.id,
                VideoViewORM.channel_id == channel_video_author.id,
                VideoViewORM.anonymous_id.is_(None),
                VideoViewORM.views_count == 1,
                VideoViewORM.created_at == get_current_utc_date(),
            )
        )
        sql_result_view_exists = await session.execute(statement=stmt)

        assert video.views_count == old_views_count
        assert not sql_result_view_exists.scalar_one()


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_video_private_and_channel_not_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
        )
        old_views_count = video.views_count

        command = CreateVideoViewCommandFactory.build(current_channel_id=None, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)

        stmt = select(
            exists().where(
                VideoViewORM.video_id == video.id,
                VideoViewORM.channel_id.is_(None),
                VideoViewORM.anonymous_id == command.anonymous_id,
                VideoViewORM.views_count == 1,
                VideoViewORM.created_at == get_current_utc_date(),
            )
        )
        sql_result_view_exists = await session.execute(statement=stmt)

        assert video.views_count == old_views_count
        assert not sql_result_view_exists.scalar_one()


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_video_views_limit_reached_and_channel_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        channel_video_author = await ChannelORMFactory.create(session=session)

        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )

        await VideoViewORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=channel.id,
            anonymous_id=None,
            views_count=VIDEO_VIEWS_LIMIT_PER_DAY,
        )

        command = CreateVideoViewCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with patch.object(use_case._video_service, 'try_increase_views_count') as mock_video_service:
            with pytest.raises(VideoViewsLimitReached):
                await use_case.execute(command=command)

        mock_video_service.assert_not_called()


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_video_views_limit_reached_and_channel_not_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel_video_author = await ChannelORMFactory.create(session=session)

        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )

        command = CreateVideoViewCommandFactory.build(current_channel_id=None, video_id=video.id)

        await VideoViewORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=None,
            anonymous_id=command.anonymous_id,
            views_count=VIDEO_VIEWS_LIMIT_PER_DAY,
        )

        with patch.object(use_case._video_service, 'try_increase_views_count') as mock_video_service:
            with pytest.raises(VideoViewsLimitReached):
                await use_case.execute(command=command)

        mock_video_service.assert_not_called()


@pytest.mark.asyncio
async def test_create_video_view_does_not_create_view_if_increase_views_count_fails(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        use_case._video_service.TRY_INCREASE_VIEWS_COUNT_RAISE_ERROR = True  # pyright: ignore[reportAttributeAccessIssue]

        channel = await ChannelORMFactory.create(session=session)
        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )

        command = CreateVideoViewCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)

        stmt = select(
            exists().where(
                VideoViewORM.video_id == command.video_id,
                VideoViewORM.channel_id == command.current_channel_id,
                VideoViewORM.anonymous_id.is_(None),
                VideoViewORM.created_at == get_current_utc_date(),
            )
        )
        sql_result_view_exists = await session.execute(statement=stmt)

        assert not sql_result_view_exists.scalar_one()


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_channel_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )

        command = CreateVideoViewCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=video.id,
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_channel_not_active(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )

        command = CreateVideoViewCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_video_not_completed(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        channel_video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel_video_author.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )

        command = CreateVideoViewCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_view_raises_error_if_video_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoViewUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = CreateVideoViewCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)
