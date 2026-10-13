from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.oauth.dto import OAuthAccount
from app.application.oauth.interfaces import IOAuthAccountReader
from app.application.oauth.queries import GetOAuthConnectedAccountsQuery
from app.domain.channels.services import IChannelService


@dataclass
class GetOAuthConnectedAccountsUseCase:
    _channel_service: IChannelService
    _oauth_account_reader: IOAuthAccountReader
    _tm: ITransactionManager

    async def execute(self, query: GetOAuthConnectedAccountsQuery) -> list[OAuthAccount]:
        async with self._tm.begin(commit=False):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=query.current_channel_id)
            return await self._oauth_account_reader.get_connected(channel_id=channel.id)
