import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.subscriptions.use_cases.unsubscribe import UnsubscribeUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
)
from app.domain.subscriptions.exceptions import SubscriptionNotFoundError
from app.infrastructure.sqlalchemy.models.channels import SubscriptionORM
from tests.factories.commands.subscriptions import UnsubscribeCommandFactory
from tests.factories.models.channels import ChannelORMFactory, SubscriptionORMFactory


@pytest.mark.asyncio
async def test_unsubscribe_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UnsubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session)
        subscribed_to = await ChannelORMFactory.create(session=session)

        db_subscription = await SubscriptionORMFactory.create(
            session=session,
            subscriber_id=subscriber.id,
            subscribed_to_id=subscribed_to.id,
        )

        command = UnsubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
            channel_slug=subscribed_to.slug,
        )

        result = await use_case.execute(command=command)

        stmt = select(SubscriptionORM).where(SubscriptionORM.id == db_subscription.id)
        db_subscription = (await session.execute(stmt)).scalar_one_or_none()

        assert result is None
        assert db_subscription is None


@pytest.mark.asyncio
async def test_unsubscribe_raises_error_if_current_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UnsubscribeUseCase)
        session = await di.get(AsyncSession)

        subscribed_to = await ChannelORMFactory.create(session=session)

        command = UnsubscribeCommandFactory.build(channel_slug=subscribed_to.slug)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_unsubscribe_raises_error_if_current_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UnsubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session, is_active=False)
        subscribed_to = await ChannelORMFactory.create(session=session)

        command = UnsubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
            channel_slug=subscribed_to.slug,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_unsubscribe_raises_error_if_channel_slug_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UnsubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session)

        command = UnsubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
        )

        with pytest.raises(ChannelNotFoundBySlugError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_unsubscribe_raises_error_if_subscription_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UnsubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session)
        subscribed_to = await ChannelORMFactory.create(session=session)

        command = UnsubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
            channel_slug=subscribed_to.slug,
        )

        with pytest.raises(SubscriptionNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_unsubscribe_raises_error_if_try_to_unsubscribe_from_self(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UnsubscribeUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = UnsubscribeCommandFactory.build(
            current_channel_id=channel.id,
            channel_slug=channel.slug,
        )

        with pytest.raises(SubscriptionNotFoundError):
            await use_case.execute(command=command)
