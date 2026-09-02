from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.interfaces.jwt import IJWTService
from app.application.oauth.interfaces.service import IOAuthServiceFactory
from app.application.oauth.use_cases.verify_code import OAuthVerifyCodeUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
)
from app.domain.oauth.exceptions import OAuthProviderAlreadyConnectedError
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.oauth import OAuthAccountORM
from tests.factories.commands.oauth import OAuthVerifyCodeCommandFactory
from tests.factories.dto.oauth import OAuthProviderUserDataFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.oauth import OAuthAcccountORMFactory
from tests.mocks.oauth.service import MockOAuthServiceFactory


@pytest.mark.asyncio
async def test_verify_code_returns_tokens_and_new_channel_and_oauth_account_created(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        session = await di.get(AsyncSession)
        jwt_service = await di.get(IJWTService)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=None,
            provider=oauth_provider_user_data.provider,
        )

        channel_stmt = select(ChannelORM).where(ChannelORM.email == oauth_provider_user_data.email)
        db_channel = (await session.execute(statement=channel_stmt)).scalar_one_or_none()
        oauth_account_stmt = select(OAuthAccountORM).where(OAuthAccountORM.provider_uid == oauth_provider_user_data.uid)
        db_oauth_account = (await session.execute(statement=oauth_account_stmt)).scalar_one_or_none()

        assert db_channel is None
        assert db_oauth_account is None

        tokens: dict[str, str] = await use_case.execute(command=command)

        channel_stmt = select(ChannelORM).where(ChannelORM.email == oauth_provider_user_data.email)
        db_channel = (await session.execute(statement=channel_stmt)).scalar_one()
        oauth_account_stmt = select(OAuthAccountORM).where(OAuthAccountORM.provider_uid == oauth_provider_user_data.uid)
        db_oauth_account = (await session.execute(statement=oauth_account_stmt)).scalar_one()

        decoded_access_token = jwt_service.decode_access_token(tokens['access'])
        decoded_refresh_token = jwt_service.decode_refresh_token(tokens['refresh'])

        assert decoded_access_token['sub'] == db_channel.id
        assert decoded_access_token['token_type'] == 'access'
        assert decoded_refresh_token['sub'] == db_channel.id
        assert decoded_refresh_token['token_type'] == 'refresh'

        assert db_channel.email == oauth_provider_user_data.email
        assert db_channel.slug == oauth_provider_user_data.login
        assert db_channel.name == oauth_provider_user_data.name
        assert db_channel.password_hash is None
        assert db_channel.description == ''
        assert db_channel.country == ''
        assert db_channel.is_active
        assert db_channel.avatar_s3_key is None

        assert db_oauth_account.channel_id == db_channel.id
        assert db_oauth_account.provider == oauth_provider_user_data.provider
        assert db_oauth_account.provider_uid == oauth_provider_user_data.uid


@pytest.mark.asyncio
async def test_verify_code_raises_error_if_channel_with_email_already_exists(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        session = await di.get(AsyncSession)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data
        await ChannelORMFactory.create(session=session, email=oauth_provider_user_data.email)

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=None,
            provider=oauth_provider_user_data.provider,
        )

        with pytest.raises(ChannelWithEmailAlreadyExistsError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_verify_code_builds_unique_slug_if_base_slug_already_exists(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        jwt_service = await di.get(IJWTService)
        session = await di.get(AsyncSession)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data
        await ChannelORMFactory.create(session=session, slug=oauth_provider_user_data.login)

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=None,
            provider=oauth_provider_user_data.provider,
        )

        tokens: dict[str, str] = await use_case.execute(command=command)

        decoded_access_token = jwt_service.decode_access_token(tokens['access'])
        decoded_refresh_token = jwt_service.decode_refresh_token(tokens['refresh'])

        channel_stmt = select(ChannelORM).where(ChannelORM.email == oauth_provider_user_data.email)
        db_channel = (await session.execute(statement=channel_stmt)).scalar_one()
        oauth_account_stmt = select(OAuthAccountORM).where(OAuthAccountORM.provider_uid == oauth_provider_user_data.uid)
        db_oauth_account = (await session.execute(statement=oauth_account_stmt)).scalar_one()

        assert decoded_access_token['sub'] == db_channel.id
        assert decoded_access_token['token_type'] == 'access'
        assert decoded_refresh_token['sub'] == db_channel.id
        assert decoded_refresh_token['token_type'] == 'refresh'

        assert db_channel.email == oauth_provider_user_data.email
        assert db_channel.slug.startswith(f'{oauth_provider_user_data.login}-')
        assert len(db_channel.slug) == len(oauth_provider_user_data.login) + 11
        assert db_channel.name == oauth_provider_user_data.name
        assert db_channel.password_hash is None
        assert db_channel.description == ''
        assert db_channel.country == ''
        assert db_channel.is_active
        assert db_channel.avatar_s3_key is None

        assert db_oauth_account.channel_id == db_channel.id
        assert db_oauth_account.provider == oauth_provider_user_data.provider
        assert db_oauth_account.provider_uid == oauth_provider_user_data.uid


@pytest.mark.asyncio
async def test_verify_code_returns_tokens_if_oauth_account_already_connected_but_channel_not_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        jwt_service = await di.get(IJWTService)
        session = await di.get(AsyncSession)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data

        db_channel = await ChannelORMFactory.create(session=session)
        await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider_uid=oauth_provider_user_data.uid,
            provider=oauth_provider_user_data.provider,
        )

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=None,
            provider=oauth_provider_user_data.provider,
        )

        tokens: dict[str, str] = await use_case.execute(command=command)

        decoded_access_token = jwt_service.decode_access_token(tokens['access'])
        decoded_refresh_token = jwt_service.decode_refresh_token(tokens['refresh'])

        assert decoded_access_token['sub'] == db_channel.id
        assert decoded_access_token['token_type'] == 'access'
        assert decoded_refresh_token['sub'] == db_channel.id
        assert decoded_refresh_token['token_type'] == 'refresh'


@pytest.mark.asyncio
async def test_verify_code_returns_none_if_new_oauth_account_connected_with_authenticated_channel(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        session = await di.get(AsyncSession)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data

        db_channel = await ChannelORMFactory.create(session=session)

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=oauth_provider_user_data.provider,
        )

        oauth_account_stmt = select(OAuthAccountORM).where(OAuthAccountORM.provider_uid == oauth_provider_user_data.uid)
        db_oauth_account = (await session.execute(statement=oauth_account_stmt)).scalar_one_or_none()
        assert db_oauth_account is None

        result = await use_case.execute(command=command)
        assert result is None

        oauth_account_stmt = select(OAuthAccountORM).where(OAuthAccountORM.provider_uid == oauth_provider_user_data.uid)
        db_oauth_account = (await session.execute(statement=oauth_account_stmt)).scalar_one()

        assert db_oauth_account.channel_id == db_channel.id
        assert db_oauth_account.provider == oauth_provider_user_data.provider


@pytest.mark.asyncio
async def test_verify_code_raises_error_if_authenticated_channel_not_active(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        session = await di.get(AsyncSession)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=oauth_provider_user_data.provider,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_verify_code_raises_error_if_authenticated_channel_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=uuid7(),
            provider=oauth_provider_user_data.provider,
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
@pytest.mark.parametrize('use_existing_channel', [True, False])
async def test_verify_code_raises_error_if_provider_already_connected_and_channel_authenticated(
    mock_container: AsyncContainer,
    use_existing_channel: bool,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthVerifyCodeUseCase)
        session = await di.get(AsyncSession)
        oauth_service_factory: MockOAuthServiceFactory = await di.get(IOAuthServiceFactory)
        oauth_provider_user_data = OAuthProviderUserDataFactory.build()
        oauth_service_factory.provider.user_data = oauth_provider_user_data

        db_channel = await ChannelORMFactory.create(session=session)
        await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider_uid=oauth_provider_user_data.uid,
            provider=oauth_provider_user_data.provider,
        )

        command = OAuthVerifyCodeCommandFactory.build(
            current_channel_id=db_channel.id if use_existing_channel else uuid7(),
            provider=oauth_provider_user_data.provider,
        )

        with pytest.raises(OAuthProviderAlreadyConnectedError):
            await use_case.execute(command=command)
