import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import AddVideoToHistoryUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.infrastructure.sqlalchemy.models import VideoHistoryItemORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import AddVideoToHistoryCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoHistoryItemORMFactory, VideoORMFactory


@pytest.mark.asyncio
async def test_add_video_to_history_returns_none_if_created(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )

        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        stmt = select(
            exists().where(VideoHistoryItemORM.video_id == video.id, VideoHistoryItemORM.channel_id == channel.id)
        )
        video_in_history = (await session.execute(statement=stmt)).scalar_one()
        assert not video_in_history

        result = await use_case.execute(command=command)
        video_in_history = (await session.execute(statement=stmt)).scalar_one()

        assert result is None
        assert video_in_history


@pytest.mark.asyncio
async def test_add_video_to_history_returns_none_if_created_and_video_private(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )

        command = AddVideoToHistoryCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        stmt = select(
            exists().where(VideoHistoryItemORM.video_id == video.id, VideoHistoryItemORM.channel_id == video_author.id)
        )
        video_in_history = (await session.execute(statement=stmt)).scalar_one()
        assert not video_in_history

        result = await use_case.execute(command=command)
        video_in_history = (await session.execute(statement=stmt)).scalar_one()

        assert result is None
        assert video_in_history


@pytest.mark.asyncio
async def test_add_video_to_history_returns_none_if_video_already_in_history(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        video_history_item = await VideoHistoryItemORMFactory.create(
            session=session, channel_id=channel.id, video_id=video.id
        )
        session.expunge(instance=video_history_item)

        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        result = await use_case.execute(command=command)

        assert result is None

        stmt = select(VideoHistoryItemORM).where(
            VideoHistoryItemORM.video_id == video.id, VideoHistoryItemORM.channel_id == channel.id
        )
        db_video_history_item = (await session.execute(statement=stmt)).scalar_one()

        assert db_video_history_item.id == video_history_item.id
        assert db_video_history_item.channel_id == video_history_item.channel_id
        assert db_video_history_item.video_id == video_history_item.video_id
        assert db_video_history_item.created_at > video_history_item.created_at


@pytest.mark.asyncio
async def test_add_video_to_history_returns_none_if_video_already_in_history_if_video_private(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        video_history_item = await VideoHistoryItemORMFactory.create(
            session=session, channel_id=video_author.id, video_id=video.id
        )
        session.expunge(instance=video_history_item)

        command = AddVideoToHistoryCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        result = await use_case.execute(command=command)

        assert result is None

        stmt = select(VideoHistoryItemORM).where(
            VideoHistoryItemORM.video_id == video.id, VideoHistoryItemORM.channel_id == video_author.id
        )
        db_video_history_item = (await session.execute(statement=stmt)).scalar_one()

        assert db_video_history_item.id == video_history_item.id
        assert db_video_history_item.channel_id == video_history_item.channel_id
        assert db_video_history_item.video_id == video_history_item.video_id
        assert db_video_history_item.created_at > video_history_item.created_at


@pytest.mark.asyncio
async def test_add_video_to_history_raises_error_if_video_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id
        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_add_video_to_history_raises_error_if_video_author_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
@pytest.mark.parametrize('upload_status', [VideoUploadStatusEnum.PENDING, VideoUploadStatusEnum.UPLOADING])
async def test_add_video_to_history_raises_error_if_video_not_completed(
    container: AsyncContainer,
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=upload_status,
        )
        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_add_video_to_history_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_add_video_to_history_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = AddVideoToHistoryCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_add_video_to_history_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AddVideoToHistoryUseCase)

        command = AddVideoToHistoryCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
