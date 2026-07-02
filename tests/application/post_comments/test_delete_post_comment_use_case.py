from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.post_comments.use_cases.delete_post_comment import (
    DeletePostCommentUseCase,
)
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.post_comments.exceptions import PostCommentAccessForbiddenError, PostCommentNotFoundByIdError
from tests.factories.commands.post_comments import DeletePostCommentCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostCommentORMFactory, PostORMFactory


@pytest.mark.asyncio
async def test_delete_post_comment_success(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        post_comment = await PostCommentORMFactory.create(
            session=session,
            channel_id=channel.id,
            post_id=post.id,
            reply_comment_id=None,
        )

        command = DeletePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_comment_id=post_comment.id,
        )

        result = await use_case.execute(command=command)

        assert result is None

        db_comment = await session.get(type(post_comment), post_comment.id)
        assert db_comment is None


@pytest.mark.asyncio
async def test_delete_post_comment_raises_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        post_comment = await PostCommentORMFactory.create(
            session=session,
            channel_id=channel.id,
            post_id=post.id,
            reply_comment_id=None,
        )

        command = DeletePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_comment_id=post_comment.id,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_post_comment_raises_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostCommentUseCase)

        command = DeletePostCommentCommandFactory.build(
            current_channel_id=uuid7(),
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_post_comment_raises_if_post_comment_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        command = DeletePostCommentCommandFactory.build(
            current_channel_id=channel.id,
            post_comment_id=uuid7(),
        )

        with pytest.raises(PostCommentNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_post_comment_raises_if_no_access(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostCommentUseCase)
        session = await di.get(AsyncSession)

        owner_channel = await ChannelORMFactory.create(session=session, is_active=True)
        other_channel = await ChannelORMFactory.create(session=session, is_active=True)
        post = await PostORMFactory.create(session=session, channel_id=other_channel.id)

        post_comment = await PostCommentORMFactory.create(
            session=session,
            channel_id=owner_channel.id,
            post_id=post.id,
            reply_comment_id=None,
        )

        command = DeletePostCommentCommandFactory.build(
            current_channel_id=other_channel.id,
            post_comment_id=post_comment.id,
        )

        with pytest.raises(PostCommentAccessForbiddenError):
            await use_case.execute(command=command)
