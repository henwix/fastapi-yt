import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.posts.use_cases.delete_post import DeletePostUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.posts.exceptions import (
    PostAccessForbiddenError,
    PostNotFoundByIdError,
)
from app.infrastructure.sqlalchemy.models.posts import PostORM
from tests.factories.commands.posts import DeletePostCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostORMFactory


@pytest.mark.asyncio
async def test_delete_post_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=db_channel.id,
        )

        command = DeletePostCommandFactory.build(
            current_channel_id=db_channel.id,
            post_id=db_post.id,
        )

        result = await use_case.execute(command=command)

        stmt = select(PostORM).where(PostORM.id == db_post.id)
        db_post = (await session.execute(stmt)).scalar_one_or_none()

        assert result is None
        assert db_post is None


@pytest.mark.asyncio
async def test_delete_post_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostUseCase)

        command = DeletePostCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_post_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=False,
        )

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=db_channel.id,
        )

        command = DeletePostCommandFactory.build(
            current_channel_id=db_channel.id,
            post_id=db_post.id,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_post_raises_error_if_post_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        command = DeletePostCommandFactory.build(
            current_channel_id=db_channel.id,
        )

        with pytest.raises(PostNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_post_raises_error_if_no_post_access(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeletePostUseCase)
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

        command = DeletePostCommandFactory.build(
            current_channel_id=another_channel.id,
            post_id=db_post.id,
        )

        with pytest.raises(PostAccessForbiddenError):
            await use_case.execute(command=command)
