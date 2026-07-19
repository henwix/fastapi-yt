from datetime import datetime
from uuid import UUID

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.sorting import SortingOrderEnum
from app.application.posts.dto import DetailedPostDTO
from app.application.posts.queries import (
    PostsSorting,
    PostsSortingFieldsEnum,
)
from app.application.posts.use_cases.get_posts import GetPostsUseCase
from app.domain.channels.exceptions import ChannelNotFoundBySlugError
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.posts import PostORMFactory
from tests.factories.queries.common import CursorPaginationFactory
from tests.factories.queries.posts import GetPostsQueryFactory


@pytest.mark.asyncio
async def test_get_posts_returns_posts_without_next_cursor_if_last_page(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetPostsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        await PostORMFactory.create_batch(
            session=session,
            size=2,
            channel_id=channel.id,
        )

        query = GetPostsQueryFactory.build(
            channel_slug=channel.slug,
            pagination=CursorPaginationFactory.build(
                cursor=Empty.UNSET,
                per_page=10,
            ),
        )

        result, next_cursor = await use_case.execute(query=query)

        assert len(result) == 2
        assert all(isinstance(x, DetailedPostDTO) for x in result)
        assert next_cursor is None


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_order', [SortingOrderEnum.ASC, SortingOrderEnum.DESC])
async def test_get_posts_returns_next_cursor_if_more_items_exist(
    container: AsyncContainer,
    expected_order: SortingOrderEnum,
):
    async with container() as di:
        use_case = await di.get(GetPostsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        await PostORMFactory.create_batch(
            session=session,
            size=3,
            channel_id=channel.id,
        )

        sorting = PostsSorting(
            sort_by=PostsSortingFieldsEnum.CREATED_AT,
            order=expected_order,
        )

        query = GetPostsQueryFactory.build(
            channel_slug=channel.slug,
            sorting=sorting,
            pagination=CursorPaginationFactory.build(
                cursor=Empty.UNSET,
                per_page=2,
            ),
        )

        result, next_cursor = await use_case.execute(query=query)

        assert len(result) == 2
        assert next_cursor is not None

        decoded = base64url_decode(next_cursor)

        assert UUID(decoded['id']) == result[-1].id
        assert datetime.fromisoformat(decoded['created_at']) == result[-1].created_at


@pytest.mark.asyncio
async def test_get_posts_returns_correct_page_by_cursor(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetPostsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        await PostORMFactory.create_batch(
            session=session,
            size=3,
            channel_id=channel.id,
        )

        sorting = PostsSorting(
            sort_by=PostsSortingFieldsEnum.CREATED_AT,
            order=SortingOrderEnum.ASC,
        )

        first_query = GetPostsQueryFactory.build(
            channel_slug=channel.slug,
            sorting=sorting,
            pagination=CursorPaginationFactory.build(
                cursor=Empty.UNSET,
                per_page=2,
            ),
        )

        first_page, cursor = await use_case.execute(query=first_query)

        assert len(first_page) == 2
        assert cursor is not None

        second_query = GetPostsQueryFactory.build(
            channel_slug=channel.slug,
            sorting=sorting,
            pagination=CursorPaginationFactory.build(
                cursor=cursor,
                per_page=2,
            ),
        )

        second_page, next_cursor = await use_case.execute(query=second_query)

        assert len(second_page) == 1
        assert next_cursor is None

        assert {x.id for x in first_page}.isdisjoint({x.id for x in second_page})


@pytest.mark.asyncio
async def test_get_posts_raises_error_if_cursor_invalid(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GetPostsUseCase)

        query = GetPostsQueryFactory.build(
            pagination=CursorPaginationFactory.build(
                cursor='invalid cursor',
                per_page=10,
            ),
        )

        with pytest.raises(InvalidCursorError):
            await use_case.execute(query=query)


@pytest.mark.asyncio
async def test_get_posts_raises_error_if_channel_not_found_by_slug(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetPostsUseCase)

        query = GetPostsQueryFactory.build(
            channel_slug='non-existing-slug',
            pagination=CursorPaginationFactory.build(),
        )

        with pytest.raises(ChannelNotFoundBySlugError):
            await use_case.execute(query=query)
