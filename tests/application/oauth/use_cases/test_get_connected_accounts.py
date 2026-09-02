import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.oauth.dto import OAuthAccount
from app.application.oauth.use_cases.get_connected_accounts import OAuthGetConnectedAccountsUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.oauth.enums import OAuthProviderEnum
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.oauth import OAuthAcccountORMFactory
from tests.factories.queries.oauth import OAuthGetConnectedAccountsQueryFactory


@pytest.mark.asyncio
async def test_get_connected_accounts_returns_empty_list_if_no_accounts_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(OAuthGetConnectedAccountsUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        query = OAuthGetConnectedAccountsQueryFactory.build(current_channel_id=db_channel.id)

        result = await use_case.execute(query=query)

        assert len(result) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_oauth_provider', [OAuthProviderEnum.GITHUB, OAuthProviderEnum.GOOGLE])
async def test_get_connected_accounts_returns_one_account(
    container: AsyncContainer,
    expected_oauth_provider: OAuthProviderEnum,
):
    async with container() as di:
        use_case = await di.get(OAuthGetConnectedAccountsUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        db_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider=expected_oauth_provider,
        )
        query = OAuthGetConnectedAccountsQueryFactory.build(current_channel_id=db_channel.id)

        result = await use_case.execute(query=query)
        oauth_account = result[0]

        assert isinstance(oauth_account, OAuthAccount)
        assert len(result) == 1
        assert oauth_account.provider is expected_oauth_provider
        assert oauth_account.created_at == db_oauth_account.created_at


@pytest.mark.asyncio
async def test_get_connected_accounts_returns_two_accounts(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(OAuthGetConnectedAccountsUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        db_github_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider=OAuthProviderEnum.GITHUB,
        )
        db_google_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider=OAuthProviderEnum.GOOGLE,
        )
        query = OAuthGetConnectedAccountsQueryFactory.build(current_channel_id=db_channel.id)

        result = await use_case.execute(query=query)

        assert len(result) == 2

        for oauth_account in result:
            assert isinstance(oauth_account, OAuthAccount)

            if oauth_account.provider is OAuthProviderEnum.GOOGLE:
                assert oauth_account.created_at == db_google_oauth_account.created_at
            if oauth_account.provider is OAuthProviderEnum.GITHUB:
                assert oauth_account.created_at == db_github_oauth_account.created_at


@pytest.mark.asyncio
async def test_get_connected_accounts_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(OAuthGetConnectedAccountsUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)
        query = OAuthGetConnectedAccountsQueryFactory.build(current_channel_id=db_channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(query=query)


@pytest.mark.asyncio
async def test_get_connected_accounts_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(OAuthGetConnectedAccountsUseCase)
        query = OAuthGetConnectedAccountsQueryFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(query=query)
