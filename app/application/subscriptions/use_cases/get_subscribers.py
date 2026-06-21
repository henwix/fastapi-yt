from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.subscriptions.dto import DetailedSubscriptionDTO
from app.application.subscriptions.interfaces.reader import ISubscriptionReader
from app.application.subscriptions.queries import GetSubscribersQuery, SubscriptionsSortFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetSubscribersUseCase:
    channel_service: IChannelService
    subscription_reader: ISubscriptionReader
    transaction_manager: ITransactionManager

    async def execute(self, query: GetSubscribersQuery) -> tuple[list[DetailedSubscriptionDTO], str | None]:
        cursor_sort_value = None
        cursor_sort_id = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)
                match query.sorting.sort_by:
                    case SubscriptionsSortFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(decoded_cursor['created_at'])
                        cursor_sort_id = UUID(decoded_cursor['id'])

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=query.current_channel_id)
            subscribers = await self.subscription_reader.get_subscribers_by_id(
                subscribed_to_id=channel.id,
                cursor_sort_value=cursor_sort_value,
                cursor_sort_id=cursor_sort_id,
                sorting=query.sorting,
                pagination=query.pagination,
            )

        next_cursor = None

        if len(subscribers) > query.pagination.per_page:
            subscribers = subscribers[: query.pagination.per_page]
            last_item = subscribers[-1]

            match query.sorting.sort_by:
                case SubscriptionsSortFieldsEnum.CREATED_AT:
                    next_cursor = {
                        'created_at': last_item.created_at.isoformat(),
                        'id': str(last_item.subscription_id),
                    }
        return subscribers, base64url_encode(value=next_cursor) if next_cursor else None
