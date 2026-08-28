from abc import ABC, abstractmethod

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
