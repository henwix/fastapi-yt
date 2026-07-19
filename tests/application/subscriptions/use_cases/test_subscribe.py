import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.subscriptions.use_cases.subscribe import SubscribeUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
)
from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.exceptions import (
    SelfSubscriptionError,
    SubscriptionAlreadyExistsError,
)
from app.infrastructure.sqlalchemy.models.channels import SubscriptionORM
from tests.factories.commands.subscriptions import SubscribeCommandFactory
from tests.factories.models.channels import ChannelORMFactory, SubscriptionORMFactory


@pytest.mark.asyncio
async def test_subscribe_returns_correct_entity_if_created(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session, is_active=True)
        subscribed_to = await ChannelORMFactory.create(session=session)

        command = SubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
            channel_slug=subscribed_to.slug,
        )

        created_subscription = await use_case.execute(command=command)

        stmt = select(SubscriptionORM).where(SubscriptionORM.id == created_subscription.id)
        result = await session.execute(statement=stmt)
        db_subscription = result.scalar_one()

        assert isinstance(created_subscription, Subscription)
        assert created_subscription.subscriber_id == subscriber.id
        assert created_subscription.subscribed_to_id == subscribed_to.id

        assert db_subscription.subscriber_id == subscriber.id
        assert db_subscription.subscribed_to_id == subscribed_to.id

        assert db_subscription.created_at == created_subscription.created_at


@pytest.mark.asyncio
async def test_subscribe_raises_error_if_self_subscription(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SubscribeUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=True)

        command = SubscribeCommandFactory.build(
            current_channel_id=db_channel.id,
            channel_slug=db_channel.slug,
        )

        with pytest.raises(SelfSubscriptionError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_subscribe_raises_error_if_current_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SubscribeUseCase)
        session = await di.get(AsyncSession)

        subscribed_to = await ChannelORMFactory.create(session=session)

        command = SubscribeCommandFactory.build(channel_slug=subscribed_to.slug)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_subscribe_raises_error_if_current_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session, is_active=False)
        subscribed_to = await ChannelORMFactory.create(session=session)

        command = SubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
            channel_slug=subscribed_to.slug,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_subscribe_raises_error_if_channel_slug_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session, is_active=True)

        command = SubscribeCommandFactory.build(current_channel_id=subscriber.id)

        with pytest.raises(ChannelNotFoundBySlugError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_subscribe_raises_error_if_subscription_already_exists(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(SubscribeUseCase)
        session = await di.get(AsyncSession)

        subscriber = await ChannelORMFactory.create(session=session, is_active=True)
        subscribed_to = await ChannelORMFactory.create(session=session)

        await SubscriptionORMFactory.create(
            session=session,
            subscriber_id=subscriber.id,
            subscribed_to_id=subscribed_to.id,
        )

        command = SubscribeCommandFactory.build(
            current_channel_id=subscriber.id,
            channel_slug=subscribed_to.slug,
        )

        with pytest.raises(SubscriptionAlreadyExistsError):
            await use_case.execute(command=command)
