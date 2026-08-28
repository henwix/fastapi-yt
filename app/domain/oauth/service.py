from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.repo import IOAuthAccountRepo


class IOAuthAccountService(ABC):
    @abstractmethod
    async def create(self, oauth_account: OAuthAccount) -> None: ...

    @abstractmethod
    async def get_by_uid_and_provider(self, uid: str, provider: OAuthProviderEnum) -> OAuthAccount | None: ...


@dataclass
class OAuthAccountService(IOAuthAccountService):
    _repo: IOAuthAccountRepo

    async def get_by_uid_and_provider(self, uid: str, provider: OAuthProviderEnum) -> OAuthAccount | None:
        return await self._repo.get_by_uid_and_provider(uid=uid, provider=provider)

    async def create(self, oauth_account: OAuthAccount) -> None:
        await self._repo.create(oauth_account=oauth_account)
