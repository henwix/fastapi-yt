from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.oauth.commands import DisconnectOAuthAccountCommand
from app.domain.channels.services import IChannelService
from app.domain.oauth.exceptions import OAuthAccountNotConnectedError
from app.domain.oauth.services import IOAuthAccountService


@dataclass
class DisconnectOAuthAccountUseCase:
    _channel_service: IChannelService
    _oauth_account_service: IOAuthAccountService
    _tm: ITransactionManager

    async def execute(self, command: DisconnectOAuthAccountCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            connected_accounts = await self._oauth_account_service.try_get_connected(channel_id=channel.id)

            if not [account for account in connected_accounts if account.provider is command.provider]:
                raise OAuthAccountNotConnectedError(channel_id=channel.id, provider=command.provider)

            await self._oauth_account_service.try_delete_by_channel_id_and_provider(
                channel_id=channel.id,
                provider=command.provider,
            )
