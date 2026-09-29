from datetime import datetime
from uuid import UUID

import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import CreateVideoReactionUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.enums import ReactionTypeEnum
from app.domain.videos.entities import VideoReaction
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.infrastructure.sqlalchemy.models import VideoReactionORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos.video_reactions import CreateVideoReactionCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory, VideoReactionORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('privacy_status', [VideoPrivacyStatusEnum.PUBLIC, VideoPrivacyStatusEnum.UNLISTED])
async def test_create_video_reaction_returns_reaction_entity_if_new_one_created(
    container: AsyncContainer,
    privacy_status: VideoPrivacyStatusEnum,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=privacy_status,
        )
        command = CreateVideoReactionCommandFactory.build(current_channel_id=current_channel.id, video_id=video.id)

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoReaction)
        assert isinstance(result.id, UUID)
        assert result.video_id == video.id
        assert result.channel_id == current_channel.id
        assert result.reaction_type is command.reaction_type
        assert isinstance(result.created_at, datetime)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('current_reaction_type', 'new_reaction_type'),
    [
        (ReactionTypeEnum.NEGATIVE, ReactionTypeEnum.POSITIVE),
        (ReactionTypeEnum.POSITIVE, ReactionTypeEnum.NEGATIVE),
    ],
)
async def test_create_video_reaction_returns_reaction_entity_if_reaction_type_updated(
    container: AsyncContainer,
    current_reaction_type: ReactionTypeEnum,
    new_reaction_type: ReactionTypeEnum,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )
        existing_reaction = await VideoReactionORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=current_channel.id,
            reaction_type=current_reaction_type.value,
        )
        session.expunge(existing_reaction)
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=current_channel.id,
            video_id=video.id,
            reaction_type=new_reaction_type,
        )

        result = await use_case.execute(command=command)

        db_reaction_stmt = select(VideoReactionORM).where(
            VideoReactionORM.video_id == video.id, VideoReactionORM.channel_id == current_channel.id
        )
        db_reaction = (await session.execute(statement=db_reaction_stmt)).scalar_one()

        assert isinstance(result, VideoReaction)
        assert result.id == existing_reaction.id
        assert result.video_id == existing_reaction.video_id
        assert result.channel_id == existing_reaction.channel_id
        assert result.reaction_type is new_reaction_type
        assert result.created_at == existing_reaction.created_at

        assert db_reaction.id == existing_reaction.id
        assert db_reaction.video_id == existing_reaction.video_id
        assert db_reaction.channel_id == existing_reaction.channel_id
        assert db_reaction.reaction_type == new_reaction_type.value
        assert db_reaction.created_at == existing_reaction.created_at


@pytest.mark.asyncio
async def test_create_video_reaction_returns_none_if_reaction_type_not_changed(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )
        existing_reaction = await VideoReactionORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=current_channel.id,
        )
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=current_channel.id,
            video_id=video.id,
            reaction_type=ReactionTypeEnum(existing_reaction.reaction_type),
        )

        result = await use_case.execute(command=command)

        db_reaction_stmt = select(VideoReactionORM).where(
            VideoReactionORM.video_id == video.id, VideoReactionORM.channel_id == current_channel.id
        )
        db_reaction = (await session.execute(statement=db_reaction_stmt)).scalar_one()

        assert result is None
        assert db_reaction.reaction_type == command.reaction_type.value


@pytest.mark.asyncio
async def test_create_video_reaction_returns_reaction_entity_if_new_one_created_and_video_private(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
        )
        command = CreateVideoReactionCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoReaction)
        assert isinstance(result.id, UUID)
        assert result.video_id == video.id
        assert result.channel_id == video_author.id
        assert result.reaction_type is command.reaction_type
        assert isinstance(result.created_at, datetime)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('current_reaction_type', 'new_reaction_type'),
    [
        (ReactionTypeEnum.NEGATIVE, ReactionTypeEnum.POSITIVE),
        (ReactionTypeEnum.POSITIVE, ReactionTypeEnum.NEGATIVE),
    ],
)
async def test_create_video_reaction_returns_reaction_entity_if_reaction_type_updated_and_video_private(
    container: AsyncContainer,
    current_reaction_type: ReactionTypeEnum,
    new_reaction_type: ReactionTypeEnum,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
        )
        existing_reaction = await VideoReactionORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=video_author.id,
            reaction_type=current_reaction_type.value,
        )
        session.expunge(existing_reaction)
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=video_author.id,
            video_id=video.id,
            reaction_type=new_reaction_type,
        )

        result = await use_case.execute(command=command)

        db_reaction_stmt = select(VideoReactionORM).where(
            VideoReactionORM.video_id == video.id, VideoReactionORM.channel_id == video_author.id
        )
        db_reaction = (await session.execute(statement=db_reaction_stmt)).scalar_one()

        assert isinstance(result, VideoReaction)
        assert result.id == existing_reaction.id
        assert result.video_id == existing_reaction.video_id
        assert result.channel_id == existing_reaction.channel_id
        assert result.reaction_type is new_reaction_type
        assert result.created_at == existing_reaction.created_at

        assert db_reaction.id == existing_reaction.id
        assert db_reaction.video_id == existing_reaction.video_id
        assert db_reaction.channel_id == existing_reaction.channel_id
        assert db_reaction.reaction_type == new_reaction_type.value
        assert db_reaction.created_at == existing_reaction.created_at


@pytest.mark.asyncio
async def test_create_video_reaction_returns_none_if_reaction_type_not_changed_and_video_private(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )
        existing_reaction = await VideoReactionORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=video_author.id,
        )
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=video_author.id,
            video_id=video.id,
            reaction_type=ReactionTypeEnum(existing_reaction.reaction_type),
        )

        result = await use_case.execute(command=command)

        db_reaction_stmt = select(VideoReactionORM).where(
            VideoReactionORM.video_id == video.id, VideoReactionORM.channel_id == video_author.id
        )
        db_reaction = (await session.execute(statement=db_reaction_stmt)).scalar_one()

        assert result is None
        assert db_reaction.reaction_type == command.reaction_type.value


@pytest.mark.asyncio
async def test_create_video_reaction_raises_error_if_video_private_and_access_forbidden(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
        )
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=current_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == current_channel.id
        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_create_video_reaction_raises_error_if_video_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session)
        command = CreateVideoReactionCommandFactory.build(current_channel_id=current_channel.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_create_video_reaction_raises_error_if_video_author_channel_deleted(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=current_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_create_video_reaction_raises_error_if_channel_deleted(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=current_channel.id,
            video_id=video.id,
        )

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_create_video_reaction_raises_error_if_channel_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )
        command = CreateVideoReactionCommandFactory.build(
            video_id=video.id,
        )

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_create_video_reaction_raises_error_if_channel_not_active(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoReactionUseCase)
        session = await di.get(AsyncSession)

        current_channel = await ChannelORMFactory.create(session=session, is_active=False)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
        )
        command = CreateVideoReactionCommandFactory.build(
            current_channel_id=current_channel.id,
            video_id=video.id,
        )

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
