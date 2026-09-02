from app.application.oauth.dto import OAuthProviderUserData
from app.application.oauth.interfaces.provider import IOAuthProvider
from app.domain.oauth.enums import OAuthProviderEnum
from tests.factories.dto.oauth import OAuthProviderUserDataFactory


class MockOAuthProvider(IOAuthProvider):
    def __init__(self) -> None:
        self.user_data = OAuthProviderUserDataFactory.build()

    @property
    def provider_name(self) -> OAuthProviderEnum:
        return self.user_data.provider

    def get_login_url(self, state: str) -> str:
        return f'https://fake-oauth.test/auth?state={state}'

    async def exchange_code(self, code: str) -> str:
        return 'fake-access-token'

    async def get_user_data(self, token: str) -> OAuthProviderUserData:
        return self.user_data
