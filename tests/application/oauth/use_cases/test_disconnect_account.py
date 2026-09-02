from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.oauth.use_cases.disconnect_account import OAuthDisconnectAccountUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import (
    OAuthAccountNotConnectedError,
    OAuthAccountUnableToDisconnectError,
    OAuthNoAccountsConnectedError,
)
from app.infrastructure.sqlalchemy.models.oauth import OAuthAccountORM
from tests.factories.commands.oauth import OAuthDisconnectAccountCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.oauth import OAuthAcccountORMFactory


@pytest.mark.asyncio
async def test_disconnect_oauth_account_returns_none_if_account_disconnected_and_channel_has_valid_password(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        db_oauth_account = await OAuthAcccountORMFactory.create(session=session, channel_id=db_channel.id)

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=OAuthProviderEnum(db_oauth_account.provider),
        )

        stmt = select(
            exists().where(
                OAuthAccountORM.id == db_oauth_account.id,
                OAuthAccountORM.provider == db_oauth_account.provider,
                OAuthAccountORM.provider_uid == db_oauth_account.provider_uid,
                OAuthAccountORM.channel_id == db_channel.id,
                OAuthAccountORM.created_at == db_oauth_account.created_at,
            )
        )
        db_oauth_account_exists = (await session.execute(statement=stmt)).scalar_one()
        assert db_oauth_account_exists

        result = await use_case.execute(command=command)
        assert result is None

        db_oauth_account_exists = (await session.execute(statement=stmt)).scalar_one()
        assert not db_oauth_account_exists


@pytest.mark.asyncio
async def test_disconnect_oauth_account_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=OAuthProviderEnum.GITHUB,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_disconnect_oauth_account_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=uuid7(),
            provider=OAuthProviderEnum.GITHUB,
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_disconnect_oauth_account_raises_error_if_no_connected_oauth_accounts_were_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=OAuthProviderEnum.GITHUB,
        )

        with pytest.raises(OAuthNoAccountsConnectedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=['connected_provider', 'not_connected_provider'],
    argvalues=[
        (OAuthProviderEnum.GITHUB, OAuthProviderEnum.GOOGLE),
        (OAuthProviderEnum.GOOGLE, OAuthProviderEnum.GITHUB),
    ],
)
async def test_disconnect_oauth_account_raises_error_if_oauth_account_not_connected(
    mock_container: AsyncContainer,
    connected_provider: OAuthProviderEnum,
    not_connected_provider: OAuthProviderEnum,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)
        db_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider=connected_provider.value,
        )

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=not_connected_provider,
        )

        stmt = select(
            exists().where(
                OAuthAccountORM.id == db_oauth_account.id,
                OAuthAccountORM.provider == db_oauth_account.provider,
                OAuthAccountORM.provider_uid == db_oauth_account.provider_uid,
                OAuthAccountORM.channel_id == db_channel.id,
                OAuthAccountORM.created_at == db_oauth_account.created_at,
            )
        )

        db_oauth_account_exists = (await session.execute(statement=stmt)).scalar_one()
        assert db_oauth_account_exists

        with pytest.raises(OAuthAccountNotConnectedError):
            await use_case.execute(command=command)

        db_oauth_account_exists = (await session.execute(statement=stmt)).scalar_one()
        assert db_oauth_account_exists


@pytest.mark.asyncio
async def test_disconnect_oauth_account_raises_error_if_channel_has_no_password_and_only_one_oauth_account_connected(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, password_hash=None)
        db_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
        )

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=OAuthProviderEnum(db_oauth_account.provider),
        )

        stmt = select(
            exists().where(
                OAuthAccountORM.id == db_oauth_account.id,
                OAuthAccountORM.provider == db_oauth_account.provider,
                OAuthAccountORM.provider_uid == db_oauth_account.provider_uid,
                OAuthAccountORM.channel_id == db_channel.id,
                OAuthAccountORM.created_at == db_oauth_account.created_at,
            )
        )

        db_oauth_account_exists = (await session.execute(statement=stmt)).scalar_one()
        assert db_oauth_account_exists

        with pytest.raises(OAuthAccountUnableToDisconnectError):
            await use_case.execute(command=command)

        db_oauth_account_exists = (await session.execute(statement=stmt)).scalar_one()
        assert db_oauth_account_exists


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=['first_provider', 'second_provider'],
    argvalues=[
        (OAuthProviderEnum.GITHUB, OAuthProviderEnum.GOOGLE),
        (OAuthProviderEnum.GOOGLE, OAuthProviderEnum.GITHUB),
    ],
)
async def test_disconnect_oauth_account_disconnected_without_password_if_more_than_one_oauth_account_connected(
    mock_container: AsyncContainer,
    first_provider: OAuthProviderEnum,
    second_provider: OAuthProviderEnum,
):
    async with mock_container() as di:
        use_case = await di.get(OAuthDisconnectAccountUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session, password_hash=None)
        first_db_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider=first_provider.value,
        )
        second_db_oauth_account = await OAuthAcccountORMFactory.create(
            session=session,
            channel_id=db_channel.id,
            provider=second_provider.value,
        )

        command = OAuthDisconnectAccountCommandFactory.build(
            current_channel_id=db_channel.id,
            provider=OAuthProviderEnum(first_db_oauth_account.provider),
        )

        first_stmt = select(exists().where(OAuthAccountORM.id == first_db_oauth_account.id))
        second_stmt = select(exists().where(OAuthAccountORM.id == second_db_oauth_account.id))

        first_db_oauth_account_exists = (await session.execute(statement=first_stmt)).scalar_one()
        second_db_oauth_account_exists = (await session.execute(statement=second_stmt)).scalar_one()
        assert first_db_oauth_account_exists
        assert second_db_oauth_account_exists

        result = await use_case.execute(command=command)

        assert db_channel.password_hash is None
        assert result is None
        first_db_oauth_account_exists = (await session.execute(statement=first_stmt)).scalar_one()
        second_db_oauth_account_exists = (await session.execute(statement=second_stmt)).scalar_one()
        assert not first_db_oauth_account_exists
        assert second_db_oauth_account_exists
