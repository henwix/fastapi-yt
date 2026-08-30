from dataclasses import dataclass

from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.oauth.commands import OAuthConvertCodeCommand
from app.application.oauth.interfaces.service import IOAuthServiceFactory
from app.domain.channels.entities import Channel
from app.domain.channels.service import IChannelService
from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.exceptions import OAuthProviderAlreadyConnectedError
from app.domain.oauth.service import IOAuthAccountService


@dataclass
class OAuthConvertCodeUseCase:
    _oauth_service_factory: IOAuthServiceFactory
    _oauth_account_service: IOAuthAccountService
    _channel_service: IChannelService
    _jwt_service: IJWTService
    _transaction_manager: ITransactionManager

    async def execute(self, command: OAuthConvertCodeCommand) -> None | dict[str, str]:
        oauth_service = self._oauth_service_factory.get(provider_name=command.provider)
        await oauth_service.validate_state(state=command.state)
        token = await oauth_service.exchange_code(code=command.code)
        provider_user_data = await oauth_service.get_user_data(token=token)

        oauth_account = await self._oauth_account_service.get_by_uid_and_provider(
            uid=provider_user_data.uid,
            provider=provider_user_data.provider,
        )

        if command.current_channel_id is not None:
            if oauth_account is not None:
                raise OAuthProviderAlreadyConnectedError(
                    channel_id=command.current_channel_id,
                    provider=oauth_account.provider,
                )
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
            new_oauth_account_entity = OAuthAccount.create(
                channel_id=channel.id,
                provider_uid=provider_user_data.uid,
                provider=provider_user_data.provider,
            )
            async with self._transaction_manager:
                await self._oauth_account_service.create(oauth_account=new_oauth_account_entity)
                return

        if oauth_account is not None:
            channel = await self._channel_service.try_get_by_id(id=oauth_account.channel_id)
            return self._jwt_service.create_tokens(sub=channel.id)

        new_channel_entity = Channel.create(
            email=provider_user_data.email,
            name=provider_user_data.name,
            slug=provider_user_data.login,
        )
        new_oauth_account_entity = OAuthAccount.create(
            channel_id=new_channel_entity.id,
            provider_uid=provider_user_data.uid,
            provider=provider_user_data.provider,
        )

        await self._channel_service.try_check_email_exists(email=new_channel_entity.email.value)
        if self._channel_service.check_slug_exists(slug=new_channel_entity.slug.value):
            unique_slug = self._channel_service.build_unique_slug(slug=new_channel_entity.slug.value)
            new_channel_entity.set_slug(value=unique_slug)

        async with self._transaction_manager:
            channel = await self._channel_service.create(channel=new_channel_entity)
            await self._oauth_account_service.create(oauth_account=new_oauth_account_entity)

        return self._jwt_service.create_tokens(sub=channel.id)
