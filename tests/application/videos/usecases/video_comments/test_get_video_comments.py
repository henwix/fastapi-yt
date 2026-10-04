import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import GetVideoCommentsUseCase
from app.domain.common.constants import Empty
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoNotFoundError
from app.utils.datetime import get_current_utc_datetime
from app.utils.videos import generate_video_id
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory
from tests.factories.queries.common import CursorPaginationFactory
from tests.factories.queries.videos.video_comments import GetVideoCommentsQueryFactory


@pytest.mark.asyncio
async def test_get_video_comments_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetVideoCommentsUseCase)
        query = GetVideoCommentsQueryFactory.build(
            video_id=generate_video_id(),
            pagination=CursorPaginationFactory.build(cursor=Empty.UNSET),
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(query=query)

        assert e.value.video_id == query.video_id


@pytest.mark.asyncio
async def test_get_video_comments_raises_error_if_video_author_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetVideoCommentsUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )
        query = GetVideoCommentsQueryFactory.build(
            video_id=video.id,
            pagination=CursorPaginationFactory.build(cursor=Empty.UNSET),
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(query=query)

        assert e.value.video_id == query.video_id


@pytest.mark.asyncio
@pytest.mark.parametrize('upload_status', [VideoUploadStatusEnum.PENDING, VideoUploadStatusEnum.UPLOADING])
async def test_get_video_comments_raises_error_if_video_not_completed(
    container: AsyncContainer,
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(GetVideoCommentsUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
            upload_status=upload_status,
        )
        query = GetVideoCommentsQueryFactory.build(
            video_id=video.id,
            pagination=CursorPaginationFactory.build(cursor=Empty.UNSET),
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(query=query)

        assert e.value.video_id == query.video_id
