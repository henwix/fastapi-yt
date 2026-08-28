from urllib.parse import urlencode

from app.application.oauth.dto import OAuthProviderUserData
from app.application.oauth.interfaces.provider import IOAuthProvider
from app.core.configs import settings
from app.domain.common.exceptions import HttpRequestError, HttpResponseError
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import (
    OAuthInvalidCodeError,
    OAuthProviderEmailNotFoundError,
    OAuthProviderEmailNotVerifiedError,
    OAuthProviderRequestError,
    OAuthProviderUidNotFoundError,
)
from app.infrastructure.http.base import IHttpClient


class GitHubOAuthProvider(IOAuthProvider):
    def __init__(self, http_client: IHttpClient) -> None:
        self._http_client = http_client
        self._github_oauth_url = 'https://github.com/login/oauth/'
        self._github_api_url = 'https://api.github.com/'
        self._scope = 'read:user user:email'
        self._redirect_uri = f'{settings.frontend_origin}{settings.oauth_github_redirect_path}'
        self._client_id = settings.oauth_github_client_id
        self._client_secret = settings.oauth_github_client_secret

    async def _provider_get_request(self, url: str, headers: dict) -> dict:
        try:
            return await self._http_client.get(url=url, headers=headers)
        except HttpRequestError as e:
            raise OAuthProviderRequestError(provider=self.provider_name, error='provider_unavailable') from e
        except HttpResponseError as e:
            match e.status_code:
                case 401:
                    raise OAuthProviderRequestError(provider=self.provider_name, error='requires_authentication') from e
                case 403:
                    raise OAuthProviderRequestError(provider=self.provider_name, error='forbidden') from e
                case 404:
                    raise OAuthProviderRequestError(provider=self.provider_name, error='resource_not_found') from e
                case _:
                    raise OAuthProviderRequestError(provider=self.provider_name, error='provider_response_error') from e

    @property
    def provider_name(self) -> OAuthProviderEnum:
        return OAuthProviderEnum.GITHUB

    def get_login_url(self, state: str) -> str:
        query_params = {
            'client_id': self._client_id,
            'redirect_uri': self._redirect_uri,
            'scope': self._scope,
            'state': state,
        }
        return f'{self._github_oauth_url}authorize?{urlencode(query_params)}'

    async def exchange_code(self, code: str) -> str:
        request_body = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'redirect_uri': self._redirect_uri,
            'code': code,
        }
        headers = {'Accept': 'application/json'}
        token_url = f'{self._github_oauth_url}access_token'
        response_data = await self._http_client.post(url=token_url, headers=headers, data=request_body)

        error = response_data.get('error')

        if error is not None:
            match error:
                case 'bad_verification_code':
                    raise OAuthInvalidCodeError(provider=self.provider_name, code=code)
                case 'unverified_user_email':
                    raise OAuthProviderEmailNotVerifiedError(provider=self.provider_name)
                case _:
                    raise OAuthProviderRequestError(provider=self.provider_name, error=error)

        access_token = response_data.get('access_token')

        if access_token is None:
            raise OAuthProviderRequestError(provider=self.provider_name, error='access_token_not_found_in_response')

        return access_token

    async def get_user_data(self, token: str) -> OAuthProviderUserData:
        user_data_url = f'{self._github_api_url}user'
        headers = {'Authorization': f'Bearer {token}123'}
        response_user_data = await self._provider_get_request(url=user_data_url, headers=headers)

        provider_uid = response_user_data.get('id')
        if provider_uid is None:
            raise OAuthProviderUidNotFoundError(provider=self.provider_name)

        provider_email = response_user_data.get('email')
        if provider_email is None:
            user_email_url = f'{user_data_url}/emails'
            user_emails = await self._provider_get_request(url=user_email_url, headers=headers)
            primary_emails: list[str] = [
                email['email'] for email in user_emails if email['primary'] and email['verified']
            ]
            if not primary_emails:
                raise OAuthProviderEmailNotFoundError(provider=self.provider_name)
            provider_email = primary_emails

        provider_login = response_user_data['login']

        provider_name = response_user_data.get('name')
        if provider_name is None:
            provider_name = provider_login

        return OAuthProviderUserData(
            uid=str(provider_uid),
            email=provider_email[0],
            login=provider_login,
            name=provider_name,
            provider=self.provider_name,
        )
