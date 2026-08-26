from dataclasses import dataclass

from app.application.oauth.interfaces.service import IOAuthServiceFactory
from app.application.oauth.queries import OAuthGetLoginUrlQuery


@dataclass
class OAuthGetLoginUrlUseCase:
    _oauth_service_factory: IOAuthServiceFactory

    async def execute(self, query: OAuthGetLoginUrlQuery) -> str:
        oauth_service = self._oauth_service_factory.get(provider_name=query.provider)
        return await oauth_service.get_login_url()
