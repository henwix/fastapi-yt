from dataclasses import dataclass

from app.application.commands.subscriptions import UnsubscribeCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService
from app.domain.subscriptions.exceptions import SubscriptionNotFoundError
from app.domain.subscriptions.services import ISubscriptionService


@dataclass
class UnsubscribeUseCase:
    channel_service: IChannelService
    subscription_service: ISubscriptionService
    transaction_manager: ITransactionManager

    async def execute(self, command: UnsubscribeCommand) -> None:
        async with self.transaction_manager:
            current_channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            if current_channel.slug == command.channel_slug:
                raise SubscriptionNotFoundError(subscriber_id=current_channel.id, subscribed_to_id=current_channel.id)

            subscribe_to_channel = await self.channel_service.try_get_by_slug(slug=command.channel_slug)
            await self.subscription_service.try_delete_by_ids(
                subscriber_id=current_channel.id,
                subscribed_to_id=subscribe_to_channel.id,
            )
