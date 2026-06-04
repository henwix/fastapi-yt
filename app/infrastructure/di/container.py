from collections.abc import AsyncGenerator
from functools import lru_cache

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.jwt import IJWTService
from app.application.common.password_hasher import IPasswordHasher
from app.application.common.transaction_manager import ITransactionManager
from app.application.use_cases.auth.login import LoginUseCase
from app.application.use_cases.channels.create_channel import CreateChannelUseCase
from app.application.use_cases.channels.delete_channel import DeleteChannelUseCase
from app.application.use_cases.channels.get_channel import GetChannelUseCase
from app.application.use_cases.channels.set_password import SetChannelPasswordUseCase
from app.application.use_cases.channels.update_channel import UpdateChannelUseCase
from app.domain.channels.repository import IChannelRepository
from app.domain.channels.services import ChannelService, IChannelService
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import async_session
from app.infrastructure.sqlalchemy.repositories.channels import SAChannelRepository
from app.infrastructure.sqlalchemy.transaction_manager import SATransactionManager


class AppProvider(Provider):
    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_async_session(self) -> AsyncGenerator[AsyncSession]:
        session = async_session()
        yield session
        await session.close()

    transaction_manager = provide(SATransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
    password_hasher = provide(PwdlibPasswordHasher, scope=Scope.APP, provides=IPasswordHasher)
    jwt_service = provide(JWTService, scope=Scope.APP, provides=IJWTService)


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    channel_repository = provide(SAChannelRepository, provides=IChannelRepository)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    channel_service = provide(ChannelService, provides=IChannelService)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    create_channel = provide(CreateChannelUseCase)
    get_channel = provide(GetChannelUseCase)
    update_channel = provide(UpdateChannelUseCase)
    delete_channel = provide(DeleteChannelUseCase)
    set_channel_password = provide(SetChannelPasswordUseCase)

    # Auth
    login = provide(LoginUseCase)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        RepositoriesProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )
