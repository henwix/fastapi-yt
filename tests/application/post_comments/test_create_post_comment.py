from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.post_comments.use_cases.create_post_comment import (
    CreatePostCommentUseCase,
)
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.constants import Empty
from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.exceptions import PostCommentNotFoundError
from app.domain.posts.exceptions import PostNotFoundError
from app.infrastructure.sqlalchemy.models.posts import PostCommentORM
from tests.factories.commands.post_comments import CreatePostCommentCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostCommentORMFactory, PostORMFactory


@pytest.mark.asyncio
async def test_create_post_comment_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_id=post.id,
            text='test comment',
            reply_comment_id=Empty.UNSET,
        )

        result = await use_case.execute(command=command)

        stmt = select(PostCommentORM).where(PostCommentORM.id == result.id)
        db_comment = (await session.execute(stmt)).scalar_one()

        assert isinstance(result, PostComment)
        assert result.text == 'test comment'
        assert result.post_id == post.id
        assert result.channel_id == channel.id
        assert result.reply_comment_id is None
        assert not result.is_edited
        assert result.reply_level == 0

        assert db_comment.text == 'test comment'
        assert db_comment.post_id == post.id
        assert db_comment.channel_id == channel.id
        assert db_comment.reply_comment_id is None
        assert not db_comment.is_edited
        assert db_comment.reply_level == 0
        assert db_comment.created_at == result.created_at


@pytest.mark.asyncio
async def test_create_post_comment_with_reply_comment(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        parent_comment = await PostCommentORMFactory.create(
            session=session,
            post_id=post.id,
            channel_id=channel.id,
            reply_comment_id=None,
            reply_level=0,
        )

        first_reply_command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_id=post.id,
            text='reply comment',
            reply_comment_id=parent_comment.id,
        )

        first_reply_result = await use_case.execute(command=first_reply_command)

        assert first_reply_result.reply_comment_id == parent_comment.id
        assert first_reply_result.reply_level == parent_comment.reply_level + 1

        second_reply_command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_id=post.id,
            text='reply comment',
            reply_comment_id=first_reply_result.id,
        )

        second_reply_result = await use_case.execute(command=second_reply_command)

        assert second_reply_result.reply_comment_id == first_reply_result.id
        assert second_reply_result.reply_level == first_reply_result.reply_level + 1

        third_reply_command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_id=post.id,
            text='reply comment',
            reply_comment_id=second_reply_result.id,
        )

        third_reply_result = await use_case.execute(command=third_reply_command)

        assert third_reply_result.reply_comment_id == second_reply_result.id
        assert third_reply_result.reply_level == second_reply_result.reply_level + 1


@pytest.mark.asyncio
async def test_create_post_comment_raises_if_reply_comment_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_id=post.id,
            reply_comment_id=uuid7(),
        )

        with pytest.raises(PostCommentNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_post_comment_raises_if_post_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
        )

        with pytest.raises(PostNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_post_comment_raises_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        command = CreatePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_id=post.id,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_post_comment_raises_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostCommentUseCase)

        command = CreatePostCommentCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
