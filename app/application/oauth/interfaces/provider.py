from abc import ABC, abstractmethod

from app.application.oauth.dto import OAuthProviderUserData
from app.domain.oauth.enums import OAuthProvidersEnum


class IOAuthProvider(ABC):
    @abstractmethod
    def get_login_url(self, state: str) -> str: ...

    @property
    @abstractmethod
    def provider_name(self) -> OAuthProvidersEnum: ...

    @abstractmethod
    async def exchange_code(self, code: str) -> str: ...

    @abstractmethod
    async def get_user_data(self, token: str) -> OAuthProviderUserData: ...


class IOAuthProviderFactory(ABC):
    @abstractmethod
    def get(self, provider_name: OAuthProvidersEnum) -> IOAuthProvider: ...
