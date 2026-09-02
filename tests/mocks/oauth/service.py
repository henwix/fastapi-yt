from dataclasses import dataclass
from uuid import uuid4

from app.application.oauth.dto import OAuthProviderUserData
from app.application.oauth.interfaces.provider import IOAuthProvider
from app.application.oauth.interfaces.service import IOAuthService, IOAuthServiceFactory
from app.domain.oauth.enums import OAuthProviderEnum
from tests.mocks.oauth.provider import MockOAuthProvider


@dataclass
class MockOAuthService(IOAuthService):
    _oauth_provider: IOAuthProvider

    async def create_state(self) -> str:
        return uuid4().hex

    async def validate_state(self, state: str) -> None:
        return

    async def get_login_url(self) -> str:
        state = await self.create_state()
        return self._oauth_provider.get_login_url(state=state)

    async def exchange_code(self, code: str) -> str:
        return await self._oauth_provider.exchange_code(code=code)

    async def get_user_data(self, token: str) -> OAuthProviderUserData:
        return await self._oauth_provider.get_user_data(token=token)


class MockOAuthServiceFactory(IOAuthServiceFactory):
    provider = MockOAuthProvider()

    def get(self, provider_name: OAuthProviderEnum) -> IOAuthService:
        return MockOAuthService(_oauth_provider=self.provider)
