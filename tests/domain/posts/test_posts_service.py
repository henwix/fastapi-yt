from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.posts.entities import Post
from app.domain.posts.exceptions import PostNotFoundError
from app.domain.posts.services import IPostService
from app.utils.datetime import get_current_utc_datetime
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostORMFactory


@pytest.mark.asyncio
async def test_try_existing_get_by_id_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IPostService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        result = await service.try_get_existing_by_id(id=post.id)

        assert isinstance(result, Post)
        assert result.id == post.id
        assert result.text == post.text
        assert result.channel_id == post.channel_id
        assert result.created_at == post.created_at


@pytest.mark.asyncio
async def test_try_existing_get_by_id_raises_error_if_post_author_channel_deleted(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IPostService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        post = await PostORMFactory.create(session=session, channel_id=channel.id)

        with pytest.raises(PostNotFoundError) as e:
            await service.try_get_existing_by_id(id=post.id)

        assert e.value.post_id == post.id


@pytest.mark.asyncio
async def test_try_existing_get_by_id_raises_error_if_post_not_found(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IPostService)

        post_id = uuid7()
        with pytest.raises(PostNotFoundError) as e:
            await service.try_get_existing_by_id(id=post_id)

        assert e.value.post_id == post_id
