from dishka import Provider, Scope, provide

from app.application.oauth.interfaces import IOAuthProviderFactory, IOAuthServiceFactory
from app.domain.oauth.services import IOAuthAccountService, OAuthAccountService
from app.infrastructure.oauth.providers import GitHubOAuthProvider, GoogleOAuthProvider, OAuthProviderFactory
from app.infrastructure.oauth.service import OAuthServiceFactory


class OAuthProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=IOAuthProviderFactory)
    def provide_oauth_provider_factory(
        self,
        github_provider: GitHubOAuthProvider,
        google_provider: GoogleOAuthProvider,
    ) -> IOAuthProviderFactory:
        return OAuthProviderFactory(
            providers=[
                github_provider,
                google_provider,
            ]
        )

    github_oauth_provider = provide(GitHubOAuthProvider)
    google_oauth_provider = provide(GoogleOAuthProvider)
    oauth_service_factory = provide(OAuthServiceFactory, provides=IOAuthServiceFactory)
    oauth_account_service = provide(OAuthAccountService, provides=IOAuthAccountService)
