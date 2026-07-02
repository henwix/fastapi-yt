import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.posts.use_cases.get_post import GetPostUseCase
from app.domain.posts.entities import Post
from app.domain.posts.exceptions import PostNotFoundByIdError
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostORMFactory
from tests.factories.queries.posts import GetPostQueryFactory


@pytest.mark.asyncio
async def test_get_post_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetPostUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            is_active=True,
        )

        db_post = await PostORMFactory.create(
            session=session,
            channel_id=channel.id,
        )

        query = GetPostQueryFactory.build(post_id=db_post.id)

        result = await use_case.execute(query=query)

        assert isinstance(result, Post)
        assert result.id == db_post.id
        assert result.channel_id == db_post.channel_id
        assert result.text == db_post.text
        assert result.created_at == db_post.created_at


@pytest.mark.asyncio
async def test_get_post_raises_error_if_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetPostUseCase)

        query = GetPostQueryFactory.build()

        with pytest.raises(PostNotFoundByIdError):
            await use_case.execute(query=query)
