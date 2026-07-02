import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.posts.use_cases.create_post import CreatePostUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.posts.entities import Post
from app.infrastructure.sqlalchemy.models.posts import PostORM
from tests.factories.commands.posts import CreatePostCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_create_post_returns_correct_entity_if_created(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        command = CreatePostCommandFactory.build(
            current_channel_id=db_channel.id,
        )

        created_post = await use_case.execute(command=command)

        stmt = select(PostORM).where(PostORM.id == created_post.id)
        result = await session.execute(statement=stmt)
        db_post = result.scalar_one()

        assert isinstance(created_post, Post)
        assert created_post.text == command.text
        assert created_post.channel_id == db_channel.id

        assert db_post.text == command.text
        assert db_post.channel_id == db_channel.id

        assert db_post.created_at == created_post.created_at


@pytest.mark.asyncio
async def test_create_post_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostUseCase)

        command = CreatePostCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_post_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreatePostUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=False,
        )

        command = CreatePostCommandFactory.build(
            current_channel_id=db_channel.id,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)
