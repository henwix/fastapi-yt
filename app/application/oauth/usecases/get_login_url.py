from dataclasses import dataclass

from app.application.oauth.interfaces import IOAuthServiceFactory
from app.application.oauth.queries import GenerateOAuthLoginUrlQuery


@dataclass
class GenerateOAuthLoginUrlUseCase:
    _oauth_service_factory: IOAuthServiceFactory

    async def execute(self, query: GenerateOAuthLoginUrlQuery) -> str:
        oauth_service = self._oauth_service_factory.get(provider_name=query.provider)
        return await oauth_service.get_login_url()
