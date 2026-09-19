from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum


class IOAuthAccountRepo(ABC):
    @abstractmethod
    async def create(self, oauth_account: OAuthAccount) -> None: ...

    @abstractmethod
    async def get_by_uid_and_provider(
        self,
        uid: str,
        provider: OAuthProviderEnum,
    ) -> OAuthAccount | None: ...

    @abstractmethod
    async def get_connected_for_update(self, channel_id: UUID) -> list[OAuthAccount]: ...

    @abstractmethod
    async def delete_by_channel_id_and_provider(
        self,
        channel_id: UUID,
        provider: OAuthProviderEnum,
    ) -> bool: ...
