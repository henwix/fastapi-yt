from collections.abc import AsyncGenerator
from functools import lru_cache

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.password_hasher import IPasswordHasher
from app.application.common.transaction_manager import ITransactionManager
from app.application.use_cases.channels.create_channel import CreateChannelUseCase
from app.domain.channels.repository import IChannelRepository
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

    transaction_manager = provide(
        SATransactionManager,
        scope=Scope.REQUEST,
        provides=ITransactionManager,
    )
    password_hasher = provide(
        PwdlibPasswordHasher,
        scope=Scope.REQUEST,
        provides=IPasswordHasher,
    )


class RepositoriesProvider(Provider):
    scope = Scope.REQUEST

    channel_repository = provide(SAChannelRepository, provides=IChannelRepository)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    create_channel = provide(CreateChannelUseCase)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        RepositoriesProvider(),
        UseCasesProvider(),
    )
