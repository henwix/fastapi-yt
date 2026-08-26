from dataclasses import dataclass

from app.application.oauth.interfaces.provider import IOAuthProvider, IOAuthProviderFactory
from app.domain.oauth.enums import OAuthProvidersEnum


@dataclass
class OAuthProviderFactory(IOAuthProviderFactory):
    providers: list[IOAuthProvider]

    def get(self, provider_name: OAuthProvidersEnum) -> IOAuthProvider:
        for provider in self.providers:
            if provider.provider_name is provider_name:
                return provider
