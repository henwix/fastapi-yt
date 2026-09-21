from dataclasses import dataclass

from app.application.oauth.dto import OAuthAccount
from app.application.oauth.interfaces import IOAuthAccountReader
from app.application.oauth.queries import GetOAuthConnectedAccountsQuery
from app.domain.channels.services import IChannelService


@dataclass
class GetOAuthConnectedAccountsUseCase:
    _channel_service: IChannelService
    _oauth_account_reader: IOAuthAccountReader

    async def execute(self, query: GetOAuthConnectedAccountsQuery) -> list[OAuthAccount]:
        channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
        accounts = await self._oauth_account_reader.get_connected(channel_id=channel.id)
        return accounts
