from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.subscriptions.commands import SubscribeCommand
from app.domain.channels.services import IChannelService
from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.exceptions import SelfSubscriptionError
from app.domain.subscriptions.services import ISubscriptionService


@dataclass
class SubscribeUseCase:
    channel_service: IChannelService
    subscription_service: ISubscriptionService
    transaction_manager: ITransactionManager

    async def execute(self, command: SubscribeCommand) -> Subscription:
        async with self.transaction_manager:
            current_channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            if current_channel.slug == command.channel_slug:
                raise SelfSubscriptionError(subscriber_id=current_channel.id)

            subscribe_to_channel = await self.channel_service.try_get_by_slug(slug=command.channel_slug)
            await self.subscription_service.check_subscription_exists(
                subscriber_id=current_channel.id,
                subscribed_to_id=subscribe_to_channel.id,
            )
            subscription_entity = Subscription.create(
                subscriber_id=current_channel.id,
                subscribed_to_id=subscribe_to_channel.id,
            )
            return await self.subscription_service.create(subscription=subscription_entity)
