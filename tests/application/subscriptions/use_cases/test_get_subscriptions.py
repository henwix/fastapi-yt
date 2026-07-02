from datetime import datetime
from uuid import UUID

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.sorting import SortingOrderEnum
from app.application.subscriptions.dto import DetailedSubscriptionDTO
from app.application.subscriptions.queries import (
    SubscriptionsSorting,
    SubscriptionsSortingFieldsEnum,
)
from app.application.subscriptions.use_cases.get_subscriptions import (
    GetSubscriptionsUseCase,
)
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode
from tests.factories.models.channels import ChannelORMFactory, SubscriptionORMFactory
from tests.factories.queries.common import CursorPaginationFactory
from tests.factories.queries.subscriptions import (
    GetSubscriptionsQueryFactory,
)


@pytest.mark.asyncio
async def test_get_subscriptions_returns_subscriptions_without_next_cursor_if_last_page(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetSubscriptionsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        subscribers = await ChannelORMFactory.create_batch(session=session, size=2)

        for sub in subscribers:
            await SubscriptionORMFactory.create(
                session=session,
                subscriber_id=channel.id,
                subscribed_to_id=sub.id,
            )

        query = GetSubscriptionsQueryFactory.build(
            current_channel_id=channel.id,
            pagination=CursorPaginationFactory.build(
                cursor=Empty.UNSET,
                per_page=10,
            ),
        )

        result, next_cursor = await use_case.execute(query=query)

        assert len(result) == 2
        assert all(isinstance(x, DetailedSubscriptionDTO) for x in result)
        assert next_cursor is None


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_order', [SortingOrderEnum.ASC, SortingOrderEnum.DESC])
async def test_get_subscriptions_returns_next_cursor_if_more_items_exist(
    container: AsyncContainer,
    expected_order: SortingOrderEnum,
):
    async with container() as di:
        use_case = await di.get(GetSubscriptionsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        subscribed_channels = await ChannelORMFactory.create_batch(session=session, size=3)

        for sub in subscribed_channels:
            await SubscriptionORMFactory.create(
                session=session,
                subscriber_id=channel.id,
                subscribed_to_id=sub.id,
            )

        sorting = SubscriptionsSorting(
            sort_by=SubscriptionsSortingFieldsEnum.CREATED_AT,
            order=expected_order,
        )

        query = GetSubscriptionsQueryFactory.build(
            current_channel_id=channel.id,
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

        assert UUID(decoded['id']) == result[-1].subscription_id
        assert datetime.fromisoformat(decoded['created_at']) == result[-1].created_at


@pytest.mark.asyncio
async def test_get_subscriptions_returns_correct_page_by_cursor(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetSubscriptionsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=True)

        subscribed_channels = await ChannelORMFactory.create_batch(session=session, size=3)

        for sub in subscribed_channels:
            await SubscriptionORMFactory.create(
                session=session,
                subscriber_id=channel.id,
                subscribed_to_id=sub.id,
            )

        sorting = SubscriptionsSorting(
            sort_by=SubscriptionsSortingFieldsEnum.CREATED_AT,
            order=SortingOrderEnum.ASC,
        )

        first_query = GetSubscriptionsQueryFactory.build(
            current_channel_id=channel.id,
            sorting=sorting,
            pagination=CursorPaginationFactory.build(
                cursor=Empty.UNSET,
                per_page=2,
            ),
        )

        first_page, cursor = await use_case.execute(query=first_query)

        assert len(first_page) == 2
        assert cursor is not None

        second_query = GetSubscriptionsQueryFactory.build(
            current_channel_id=channel.id,
            sorting=sorting,
            pagination=CursorPaginationFactory.build(
                cursor=cursor,
                per_page=2,
            ),
        )

        second_page, next_cursor = await use_case.execute(query=second_query)

        assert len(second_page) == 1
        assert next_cursor is None

        assert {x.subscription_id for x in first_page}.isdisjoint({x.subscription_id for x in second_page})


@pytest.mark.asyncio
async def test_get_subscriptions_raises_error_if_cursor_invalid(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetSubscriptionsUseCase)

        query = GetSubscriptionsQueryFactory.build(
            pagination=CursorPaginationFactory.build(
                cursor='invalid cursor',
                per_page=10,
            ),
        )

        with pytest.raises(InvalidCursorError):
            await use_case.execute(query=query)


@pytest.mark.asyncio
async def test_get_subscriptions_raises_error_if_current_channel_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetSubscriptionsUseCase)

        query = GetSubscriptionsQueryFactory.build(
            pagination=CursorPaginationFactory.build(),
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(query=query)


@pytest.mark.asyncio
async def test_get_subscriptions_raises_error_if_current_channel_not_active(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GetSubscriptionsUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        query = GetSubscriptionsQueryFactory.build(
            current_channel_id=channel.id,
            pagination=CursorPaginationFactory.build(),
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(query=query)
