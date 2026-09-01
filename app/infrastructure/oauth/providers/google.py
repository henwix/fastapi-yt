from urllib.parse import unquote, urlencode

from app.application.common.interfaces.jwt import IJWTService
from app.application.oauth.dto import OAuthProviderUserData
from app.application.oauth.interfaces.provider import IOAuthProvider
from app.core.configs import settings
from app.domain.auth.exceptions import JWTInvalidTokenError
from app.domain.common.exceptions import HttpRequestError, HttpResponseError
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import (
    OAuthInvalidCodeError,
    OAuthProviderEmailNotVerifiedError,
    OAuthProviderRequestError,
    OAuthProviderResponseError,
)
from app.infrastructure.http.base import IHttpClient


class GoogleOAuthProvider(IOAuthProvider):
    def __init__(self, _http_client: IHttpClient, _jwt_service: IJWTService) -> None:
        self._http_client = _http_client
        self._jwt_service = _jwt_service
        self._google_oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self._google_token_url = 'https://oauth2.googleapis.com/token'
        self._scope = 'email openid profile'
        self._response_type = 'code'
        self._access_type = 'offline'
        self._grant_type = 'authorization_code'
        self._redirect_uri = f'{settings.frontend_origin}{settings.oauth_redirect_path}'
        self._client_id = settings.oauth_google_client_id
        self._client_secret = settings.oauth_google_client_secret

    @property
    def provider_name(self) -> OAuthProviderEnum:
        return OAuthProviderEnum.GOOGLE

    def get_login_url(self, state: str) -> str:
        query_params = {
            'client_id': self._client_id,
            'redirect_uri': self._redirect_uri,
            'response_type': self._response_type,
            'scope': self._scope,
            'access_type': self._access_type,
            'state': state,
        }
        return f'{self._google_oauth_url}?{urlencode(query_params)}'

    async def exchange_code(self, code: str) -> str:
        request_body = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'code': unquote(code),
            'grant_type': self._grant_type,
            'redirect_uri': self._redirect_uri,
        }
        try:
            response = await self._http_client.post(url=self._google_token_url, data=request_body)
        except HttpRequestError as e:
            raise OAuthProviderRequestError(provider=self.provider_name, error='provider_unavailable') from e

        except HttpResponseError as e:
            raise OAuthInvalidCodeError(provider=self.provider_name, code=code) from e

        if 'id_token' not in response:
            raise OAuthProviderResponseError(provider=self.provider_name, error='id_token_not_found_in_response')

        return response['id_token']

    async def get_user_data(self, token: str) -> OAuthProviderUserData:
        try:
            token_payload = self._jwt_service.decode_unverified_token(token=token)
        except JWTInvalidTokenError as e:
            raise OAuthProviderResponseError(provider=self.provider_name, error='unable_to_decode_openid_token') from e

        email_verified = token_payload.get('email_verified')
        if email_verified is None:
            raise OAuthProviderResponseError(
                provider=self.provider_name,
                error='email_verified_not_found_in_openid_token_payload',
            )
        if not email_verified:
            raise OAuthProviderEmailNotVerifiedError(provider=self.provider_name)

        try:
            return OAuthProviderUserData(
                uid=token_payload['sub'],
                email=token_payload['email'],
                login=token_payload['name'],
                name=token_payload['name'],
                provider=self.provider_name,
            )
        except KeyError as e:
            raise OAuthProviderResponseError(
                provider=self.provider_name, error=f'{e.args[0]}_not_found_in_openid_token_payload'
            )
