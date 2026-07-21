import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.login import LoginUseCase
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.auth.exceptions import IncorrectEmailOrPasswordError
from tests.factories.commands.auth import LoginCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_login_returns_tokens_if_credentials_are_correct(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(LoginUseCase)
        session = await di.get(AsyncSession)
        jwt_service = await di.get(IJWTService)
        password_hasher = await di.get(IPasswordHasher)

        password = 'password123'

        db_channel = await ChannelORMFactory.create(
            session=session,
            password_hash=password_hasher.get_password_hash(password),
        )

        command = LoginCommandFactory.build(
            email=db_channel.email,
            password=password,
        )

        tokens = await use_case.execute(command=command)

        assert tokens == jwt_service.create_tokens(sub=db_channel.id)


@pytest.mark.asyncio
async def test_login_raises_error_if_email_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(LoginUseCase)

        command = LoginCommandFactory.build()

        with pytest.raises(IncorrectEmailOrPasswordError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_login_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(LoginUseCase)
        session = await di.get(AsyncSession)
        password_hasher = await di.get(IPasswordHasher)

        password = 'password123'

        db_channel = await ChannelORMFactory.create(
            session=session,
            is_active=False,
            password_hash=password_hasher.get_password_hash(password),
        )

        command = LoginCommandFactory.build(
            email=db_channel.email,
            password=password,
        )

        with pytest.raises(IncorrectEmailOrPasswordError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_login_raises_error_if_password_is_incorrect(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(LoginUseCase)
        session = await di.get(AsyncSession)

        db_channel = await ChannelORMFactory.create(session=session)

        command = LoginCommandFactory.build(
            email=db_channel.email,
            password='wrong-password',
        )

        with pytest.raises(IncorrectEmailOrPasswordError):
            await use_case.execute(command=command)
