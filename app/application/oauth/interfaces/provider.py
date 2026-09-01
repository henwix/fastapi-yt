from abc import ABC, abstractmethod

from app.application.oauth.dto import OAuthProviderUserData
from app.domain.oauth.enums import OAuthProviderEnum


class IOAuthProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> OAuthProviderEnum: ...

    @abstractmethod
    def get_login_url(self, state: str) -> str: ...

    @abstractmethod
    async def exchange_code(self, code: str) -> str: ...

    @abstractmethod
    async def get_user_data(self, token: str) -> OAuthProviderUserData: ...


class IOAuthProviderFactory(ABC):
    @abstractmethod
    def get(self, provider_name: OAuthProviderEnum) -> IOAuthProvider: ...
