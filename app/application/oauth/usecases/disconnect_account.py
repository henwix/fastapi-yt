from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.oauth.commands import OAuthDisconnectAccountCommand
from app.domain.channels.service import IChannelService
from app.domain.oauth.exceptions import OAuthAccountNotConnectedError, OAuthAccountUnableToDisconnectError
from app.domain.oauth.service import IOAuthAccountService


@dataclass
class OAuthDisconnectAccountUseCase:
    _channel_service: IChannelService
    _oauth_account_service: IOAuthAccountService
    _transaction_manager: ITransactionManager

    async def execute(self, command: OAuthDisconnectAccountCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        connected_accounts = await self._oauth_account_service.try_get_connected_for_update(channel_id=channel.id)

        if not [account for account in connected_accounts if account.provider is command.provider]:
            raise OAuthAccountNotConnectedError(channel_id=channel.id, provider=command.provider)
        if channel.password_hash is None and len(connected_accounts) == 1:
            raise OAuthAccountUnableToDisconnectError(channel_id=channel.id, provider=command.provider)

        async with self._transaction_manager:
            await self._oauth_account_service.try_delete_by_channel_id_and_provider(
                channel_id=channel.id,
                provider=command.provider,
            )
