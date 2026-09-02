import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.login_channel import LoginChannelUseCase
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.auth.exceptions import IncorrectEmailOrPasswordError
from tests.factories.commands.auth import LoginChannelCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_login_channel_returns_tokens_if_credentials_are_correct(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(LoginChannelUseCase)
        session = await di.get(AsyncSession)
        jwt_service = await di.get(IJWTService)
        password_hasher = await di.get(IPasswordHasher)

        password = 'password123'

        db_channel = await ChannelORMFactory.create(
            session=session,
            password_hash=password_hasher.get_password_hash(password),
        )

        command = LoginChannelCommandFactory.build(
            email=db_channel.email,
            password=password,
        )

        tokens = await use_case.execute(command=command)

        assert tokens == jwt_service.create_tokens(sub=db_channel.id)


@pytest.mark.asyncio
async def test_login_channel_returns_tokens_if_credentials_are_correct_and_channel_not_active(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(LoginChannelUseCase)
        jwt_service = await di.get(IJWTService)
        session = await di.get(AsyncSession)
        password_hasher = await di.get(IPasswordHasher)

        password = 'password123'

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=False,
            password_hash=password_hasher.get_password_hash(password),
        )

        command = LoginChannelCommandFactory.build(
            email=db_channel.email,
            password=password,
        )

        tokens = await use_case.execute(command=command)

        assert tokens == jwt_service.create_tokens(sub=db_channel.id)


@pytest.mark.asyncio
async def test_login_channel_raises_error_if_email_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(LoginChannelUseCase)

        command = LoginChannelCommandFactory.build()

        with pytest.raises(IncorrectEmailOrPasswordError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_login_channel_raises_error_if_password_is_incorrect(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(LoginChannelUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)

        command = LoginChannelCommandFactory.build(
            email=db_channel.email,
            password='wrong-password',
        )

        with pytest.raises(IncorrectEmailOrPasswordError):
            await use_case.execute(command=command)
