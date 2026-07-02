import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.posts.use_cases.update_post import UpdatePostUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.common.constants import Empty
from app.domain.posts.entities import Post
from app.domain.posts.exceptions import (
    PostAccessForbiddenError,
    PostNotFoundByIdError,
)
from app.infrastructure.sqlalchemy.models.posts import PostORM
from tests.factories.commands.posts import UpdatePostCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostORMFactory


@pytest.mark.asyncio
async def test_update_post_returns_correct_entity_if_updated(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdatePostUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=channel.id,
        )

        command = UpdatePostCommandFactory.build(
            current_channel_id=channel.id,
            post_id=db_post.id,
            text='updated text',
        )

        result = await use_case.execute(command=command)

        stmt = select(PostORM).where(PostORM.id == db_post.id)
        updated_db_post = (await session.execute(stmt)).scalar_one()

        assert isinstance(result, Post)
        assert result.text == command.text
        assert updated_db_post.text == command.text


@pytest.mark.asyncio
async def test_update_post_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdatePostUseCase)

        command = UpdatePostCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_update_post_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdatePostUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            is_active=False,
        )

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=channel.id,
        )

        command = UpdatePostCommandFactory.build(
            current_channel_id=channel.id,
            post_id=db_post.id,
            text='new text',
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_update_post_raises_error_if_post_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdatePostUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        command = UpdatePostCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(PostNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_update_post_raises_error_if_no_post_access(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdatePostUseCase)
        session = await di.get(AsyncSession)

        owner = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        another_channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=owner.id,
        )

        command = UpdatePostCommandFactory.build(
            current_channel_id=another_channel.id,
            post_id=db_post.id,
            text='hack attempt',
        )

        with pytest.raises(PostAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_update_post_does_not_change_text_if_unset(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdatePostUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=channel.id,
            text='original text',
        )

        command = UpdatePostCommandFactory.build(
            current_channel_id=channel.id,
            post_id=db_post.id,
            text=Empty.UNSET,
        )

        result = await use_case.execute(command=command)

        assert result.text == 'original text'
