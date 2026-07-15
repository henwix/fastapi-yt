from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.subscriptions.dto import DetailedSubscriptionDTO
from app.application.subscriptions.interfaces.reader import ISubscriptionReader
from app.application.subscriptions.queries import GetSubscribersQuery, SubscriptionsSortingFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetSubscribersUseCase:
    _channel_service: IChannelService
    _subscription_reader: ISubscriptionReader

    async def execute(self, query: GetSubscribersQuery) -> tuple[list[DetailedSubscriptionDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)

                cursor_id_value = UUID(decoded_cursor['id'])

                match query.sorting.sort_by:
                    case SubscriptionsSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[SubscriptionsSortingFieldsEnum.CREATED_AT.value]
                        )

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
        subscribers = await self._subscription_reader.get_subscribers_by_id(
            subscribed_to_id=channel.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(subscribers) > query.pagination.per_page:
            subscribers = subscribers[: query.pagination.per_page]
            last_item = subscribers[-1]
            next_cursor = {'id': str(last_item.subscription_id)}

            match query.sorting.sort_by:
                case SubscriptionsSortingFieldsEnum.CREATED_AT:
                    next_cursor[SubscriptionsSortingFieldsEnum.CREATED_AT.value] = last_item.created_at.isoformat()

        return subscribers, base64url_encode(value=next_cursor) if next_cursor else None
