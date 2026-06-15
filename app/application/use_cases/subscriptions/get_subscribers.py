from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.queries.subscriptions import GetSubscribersQuery, GetSubscribersSortFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.repositories import ISubscriptionRepository
from app.utils.base64url import base64url_decode


@dataclass
class GetSubscribersUseCase:
    channel_service: IChannelService
    subscription_repo: ISubscriptionRepository
    transaction_manager: ITransactionManager

    async def execute(self, query: GetSubscribersQuery) -> tuple[list[Subscription], dict | None]:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=query.current_channel_id)

            cursor_sort_value = None
            cursor_sort_id = None

            if query.pagination.cursor is not Empty.UNSET:
                try:
                    decoded_cursor = base64url_decode(value=query.pagination.cursor)
                    match query.sorting.sort_by:
                        case GetSubscribersSortFieldsEnum.created_at:
                            cursor_sort_value = datetime.fromisoformat(decoded_cursor['created_at'])
                            cursor_sort_id = UUID(decoded_cursor['id'])

                except Exception as e:
                    raise InvalidCursorError(cursor=query.pagination.cursor) from e

            subscribers = await self.subscription_repo.get_many_by_subscribed_to_id(
                subscribed_to_id=channel.id,
                cursor_sort_value=cursor_sort_value,
                cursor_sort_id=cursor_sort_id,
                sort_by=query.sorting.sort_by.value,
                order=query.sorting.order.value,
                per_page=query.pagination.per_page,
            )

        next_cursor = None
        if subscribers and len(subscribers) > query.pagination.per_page:
            subscribers = subscribers[: query.pagination.per_page]
            last_item = subscribers[-1]
            match query.sorting.sort_by:
                case GetSubscribersSortFieldsEnum.created_at:
                    next_cursor = {
                        'created_at': last_item.created_at.isoformat(),
                        'id': str(last_item.id),
                    }
        return subscribers, next_cursor
