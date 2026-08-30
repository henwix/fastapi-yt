from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import OAuthAccountNotConnectedError, OAuthNoAccountsConnectedError
from app.domain.oauth.repo import IOAuthAccountRepo


class IOAuthAccountService(ABC):
    @abstractmethod
    async def create(self, oauth_account: OAuthAccount) -> None: ...

    @abstractmethod
    async def get_by_uid_and_provider(self, uid: str, provider: OAuthProviderEnum) -> OAuthAccount | None: ...

    @abstractmethod
    async def try_get_connected_for_update(self, channel_id: UUID) -> list[OAuthAccount]: ...

    @abstractmethod
    async def try_delete_by_channel_id_and_provider(self, channel_id: UUID, provider: OAuthProviderEnum) -> None: ...


@dataclass
class OAuthAccountService(IOAuthAccountService):
    _repo: IOAuthAccountRepo

    async def get_by_uid_and_provider(self, uid: str, provider: OAuthProviderEnum) -> OAuthAccount | None:
        return await self._repo.get_by_uid_and_provider(uid=uid, provider=provider)

    async def create(self, oauth_account: OAuthAccount) -> None:
        await self._repo.create(oauth_account=oauth_account)

    async def try_get_connected_for_update(self, channel_id: UUID) -> list[OAuthAccount]:
        connected_accounts = await self._repo.get_connected_for_update(channel_id=channel_id)
        if not connected_accounts:
            raise OAuthNoAccountsConnectedError(channel_id=channel_id)
        return connected_accounts

    async def try_delete_by_channel_id_and_provider(self, channel_id: UUID, provider: OAuthProviderEnum) -> None:
        is_deleted = await self._repo.delete_by_channel_id_and_provider(channel_id=channel_id, provider=provider)
        if not is_deleted:
            raise OAuthAccountNotConnectedError(channel_id=channel_id, provider=provider)
