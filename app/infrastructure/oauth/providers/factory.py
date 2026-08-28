from dataclasses import dataclass

from app.application.oauth.interfaces.provider import IOAuthProvider, IOAuthProviderFactory
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import OAuthProviderNotSupportedError


@dataclass
class OAuthProviderFactory(IOAuthProviderFactory):
    providers: list[IOAuthProvider]

    def get(self, provider_name: OAuthProviderEnum) -> IOAuthProvider:
        for provider in self.providers:
            if provider.provider_name is provider_name:
                return provider
        raise OAuthProviderNotSupportedError
