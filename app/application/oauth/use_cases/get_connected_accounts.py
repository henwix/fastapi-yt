from dataclasses import dataclass
from logging import getLogger

from app.application.oauth.dto import OAuthAccount
from app.application.oauth.interfaces.reader import IOAuthAccountReader
from app.application.oauth.queries import OAuthGetConnectedAccountsQuery
from app.domain.channels.service import IChannelService

logger = getLogger(__name__)


@dataclass
class OAuthGetConnectedAccountsUseCase:
    _channel_service: IChannelService
    _oauth_account_reader: IOAuthAccountReader

    async def execute(self, query: OAuthGetConnectedAccountsQuery) -> list[OAuthAccount]:
        channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
        accounts = await self._oauth_account_reader.get_connected(channel_id=channel.id)
        return accounts
