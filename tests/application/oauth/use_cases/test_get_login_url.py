from urllib.parse import parse_qs, urlencode, urlparse

import pytest
from dishka import AsyncContainer

from app.application.oauth.use_cases.get_login_url import OAuthGetLoginUrlUseCase
from app.core.configs import Settings
from app.domain.common.repos.kv import IKVRepo
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import OAuthProviderNotSupportedError
from tests.factories.queries.oauth import OAuthGetLoginUrlQueryFactory


@pytest.mark.asyncio
async def test_oauth_get_login_url_returns_correct_github_provider_login_url(
    container: AsyncContainer,
    test_settings: Settings,
):
    async with container() as di:
        use_case = await di.get(OAuthGetLoginUrlUseCase)
        kv_repo = await di.get(IKVRepo)

        query = OAuthGetLoginUrlQueryFactory.build(provider=OAuthProviderEnum.GITHUB)

        login_url = await use_case.execute(query=query)
        parsed_url = urlparse(url=login_url)
        parsed_state = parse_qs(parsed_url.query)['state'][0]

        expected_query_params = {
            'client_id': test_settings.oauth_github_client_id,
            'redirect_uri': f'{test_settings.frontend_origin}{test_settings.oauth_redirect_path}',
            'scope': 'read:user user:email',
            'state': parsed_state,
        }
        assert login_url == f'https://github.com/login/oauth/authorize?{urlencode(expected_query_params)}'

        saved_state = await kv_repo.get(key=f'oauth:state:{OAuthProviderEnum.GITHUB}:{parsed_state}')
        assert saved_state is not None
        assert saved_state == parsed_state


@pytest.mark.asyncio
async def test_oauth_get_login_url_returns_correct_google_provider_login_url(
    container: AsyncContainer,
    test_settings: Settings,
):
    async with container() as di:
        use_case = await di.get(OAuthGetLoginUrlUseCase)
        kv_repo = await di.get(IKVRepo)

        query = OAuthGetLoginUrlQueryFactory.build(provider=OAuthProviderEnum.GOOGLE)

        login_url = await use_case.execute(query=query)
        parsed_url = urlparse(url=login_url)
        parsed_state = parse_qs(parsed_url.query)['state'][0]

        expected_query_params = {
            'client_id': test_settings.oauth_google_client_id,
            'redirect_uri': f'{test_settings.frontend_origin}{test_settings.oauth_redirect_path}',
            'response_type': 'code',
            'scope': 'email openid profile',
            'access_type': 'offline',
            'state': parsed_state,
        }
        assert login_url == f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(expected_query_params)}'

        saved_state = await kv_repo.get(key=f'oauth:state:{OAuthProviderEnum.GOOGLE}:{parsed_state}')
        assert saved_state is not None
        assert saved_state == parsed_state


@pytest.mark.asyncio
async def test_oauth_get_login_url_raises_error_if_invalid_provider(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(OAuthGetLoginUrlUseCase)

        query = OAuthGetLoginUrlQueryFactory.build(provider='123')

        with pytest.raises(OAuthProviderNotSupportedError):
            await use_case.execute(query=query)
