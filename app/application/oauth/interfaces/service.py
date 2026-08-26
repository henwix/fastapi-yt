from abc import ABC, abstractmethod

from app.application.oauth.dto import OAuthProviderUserData
from app.domain.oauth.enums import OAuthProvidersEnum


class IOAuthService(ABC):
    @abstractmethod
    async def create_state(self) -> str: ...

    @abstractmethod
    async def validate_state(self, state: str) -> None: ...

    @abstractmethod
    async def get_login_url(self) -> str: ...

    @abstractmethod
    async def exchange_code(self, code: str) -> str: ...

    @abstractmethod
    async def get_user_data(self, token: str) -> OAuthProviderUserData: ...


class IOAuthServiceFactory(ABC):
    @abstractmethod
    def get(self, provider_name: OAuthProvidersEnum) -> IOAuthService: ...
