from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.dto import DetailedVideo
from app.application.videos.usecases import GetVideoUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.utils.datetime import get_current_utc_datetime
from app.utils.videos import generate_video_id
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory
from tests.factories.queries.videos import GetVideoQueryFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('privacy_status', [VideoPrivacyStatusEnum.PUBLIC, VideoPrivacyStatusEnum.UNLISTED])
async def test_get_video_returns_correct_entity_without_auth_if_video_completed_and_not_private(
    container: AsyncContainer,
    privacy_status: VideoPrivacyStatusEnum,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=privacy_status,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        query = GetVideoQueryFactory.build(current_channel_id=None, video_id=video.id)

        with patch.object(use_case._channel_service, 'try_get_existing_by_id_for_auth') as channel_service_mock:
            result = await use_case.execute(query=query)

        channel_service_mock.assert_not_called()
        assert isinstance(result, DetailedVideo)

        assert result.id == video.id
        assert result.title == video.title
        assert result.description == video.description
        assert result.privacy_status == video.privacy_status
        assert result.is_reported == video.is_reported
        assert result.created_at == video.created_at
        assert result.views_count == video.views_count
        assert result.thumbnail_s3_key == video.thumbnail_s3_key
        assert result.channel_id == channel.id
        assert result.channel_name == channel.name
        assert result.channel_slug == channel.slug


@pytest.mark.asyncio
async def test_get_video_returns_correct_entity_with_auth_if_video_completed_and_private(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        query = GetVideoQueryFactory.build(current_channel_id=channel.id, video_id=video.id)

        result = await use_case.execute(query=query)

        assert isinstance(result, DetailedVideo)

        assert result.id == video.id
        assert result.title == video.title
        assert result.description == video.description
        assert result.privacy_status == video.privacy_status
        assert result.is_reported == video.is_reported
        assert result.created_at == video.created_at
        assert result.views_count == video.views_count
        assert result.thumbnail_s3_key == video.thumbnail_s3_key
        assert result.channel_id == channel.id
        assert result.channel_name == channel.name
        assert result.channel_slug == channel.slug


@pytest.mark.asyncio
@pytest.mark.parametrize('is_authenticated', [True, False])
async def test_get_video_raises_error_if_video_private_and_access_forbidden(
    container: AsyncContainer,
    is_authenticated: bool,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        second_channel = await ChannelORMFactory.create(session=session)
        author_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        query = GetVideoQueryFactory.build(
            current_channel_id=second_channel.id if is_authenticated else None, video_id=video.id
        )

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(query=query)

        assert e.value.channel_id == query.current_channel_id
        assert e.value.video_id == query.video_id


@pytest.mark.asyncio
async def test_get_video_raises_error_if_video_private_and_current_channel_not_active(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        second_channel = await ChannelORMFactory.create(session=session, is_active=False)
        author_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        query = GetVideoQueryFactory.build(current_channel_id=second_channel.id, video_id=video.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(query=query)

        assert e.value.channel_id == query.current_channel_id


@pytest.mark.asyncio
async def test_get_video_raises_error_if_video_private_and_current_channel_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        author_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        channel_id = uuid7()
        query = GetVideoQueryFactory.build(current_channel_id=channel_id, video_id=video.id)

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(query=query)

        assert e.value.channel_id == query.current_channel_id


@pytest.mark.asyncio
async def test_get_video_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        channel_id = uuid7()
        video_id = generate_video_id()
        query = GetVideoQueryFactory.build(current_channel_id=channel_id, video_id=video_id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(query=query)

        assert e.value.video_id == query.video_id


@pytest.mark.asyncio
async def test_get_video_raises_error_if_video_author_channel_deleted(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        author_channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        query = GetVideoQueryFactory.build(current_channel_id=None, video_id=video.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(query=query)

        assert e.value.video_id == query.video_id


@pytest.mark.asyncio
@pytest.mark.parametrize('upload_status', [VideoUploadStatusEnum.PENDING, VideoUploadStatusEnum.UPLOADING])
async def test_get_video_raises_error_if_video_not_completed(
    container: AsyncContainer,
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(GetVideoUseCase)
        session = await di.get(AsyncSession)
        author_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=upload_status,
        )
        query = GetVideoQueryFactory.build(current_channel_id=None, video_id=video.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(query=query)

        assert e.value.video_id == query.video_id
