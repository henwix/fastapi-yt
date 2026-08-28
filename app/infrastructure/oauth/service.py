from dataclasses import dataclass
from uuid import uuid4

from app.application.oauth.dto import OAuthProviderUserData
from app.application.oauth.interfaces.provider import IOAuthProvider, IOAuthProviderFactory
from app.application.oauth.interfaces.service import IOAuthService, IOAuthServiceFactory
from app.domain.common.repos.kv import IKVRepo
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import OAuthInvalidStateError


@dataclass
class OAuthService(IOAuthService):
    _oauth_provider: IOAuthProvider
    _kv_repo: IKVRepo

    def _build_state_key(self, state: str) -> str:
        return f'oauth:state:{self._oauth_provider.provider_name}:{state}'

    async def create_state(self) -> str:
        state = uuid4().hex
        key = self._build_state_key(state=state)
        await self._kv_repo.set(key=key, value=state, ttl=60 * 10)
        return state

    async def validate_state(self, state: str) -> None:
        key = self._build_state_key(state=state)
        cached_state = await self._kv_repo.get(key)
        if cached_state is None:
            raise OAuthInvalidStateError(provider=self._oauth_provider.provider_name, state=state)
        await self._kv_repo.delete(key=key)

    async def get_login_url(self) -> str:
        state = await self.create_state()
        return self._oauth_provider.get_login_url(state=state)

    async def exchange_code(self, code: str) -> str:
        return await self._oauth_provider.exchange_code(code=code)

    async def get_user_data(self, token: str) -> OAuthProviderUserData:
        return await self._oauth_provider.get_user_data(token=token)


@dataclass
class OAuthServiceFactory(IOAuthServiceFactory):
    _kv_repo: IKVRepo
    _oauth_provider_factory: IOAuthProviderFactory

    def get(self, provider_name: OAuthProviderEnum) -> IOAuthService:
        provider = self._oauth_provider_factory.get(provider_name=provider_name)
        return OAuthService(_kv_repo=self._kv_repo, _oauth_provider=provider)
