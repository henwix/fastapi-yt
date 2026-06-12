from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.queries.subscriptions import GetSubscribersQuery
from app.domain.channels.services import IChannelService
from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.repositories import ISubscriptionRepository


@dataclass
class GetSubscribersUseCase:
    channel_service: IChannelService
    subscription_repo: ISubscriptionRepository
    transaction_manager: ITransactionManager

    async def execute(self, query: GetSubscribersQuery) -> list[Subscription]:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=query.current_channel_id)
            return await self.subscription_repo.get_many_by_subscribed_to_id(
                subscribed_to_id=channel.id,
                order=query.sorting.order,
                cursor=query.pagination.cursor,
                per_page=query.pagination.per_page,
            )
