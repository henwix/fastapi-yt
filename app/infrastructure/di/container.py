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
from app.application.use_cases.post_reactions.create_post_reaction import CreatePostReactionUseCase
from app.application.use_cases.post_reactions.delete_post_reaction import DeletePostReactionUseCase
from app.application.use_cases.posts.create_post import CreatePostUseCase
from app.application.use_cases.posts.delete_post import DeletePostUseCase
from app.application.use_cases.posts.get_post import GetPostUseCase
from app.application.use_cases.posts.update_post import UpdatePostUseCase
from app.application.use_cases.subscriptions.get_subscribers import GetSubscribersUseCase
from app.application.use_cases.subscriptions.subscribe import SubscribeUseCase
from app.application.use_cases.subscriptions.unsubscribe import UnsubscribeUseCase
from app.domain.channels.repositories import IChannelRepository
from app.domain.channels.services import ChannelService, IChannelService
from app.domain.post_reactions.repositories import IPostReactionRepository
from app.domain.post_reactions.services import IPostReactionService, PostReactionService
from app.domain.posts.repositories import IPostRepository
from app.domain.posts.services import IPostService, PostService
from app.domain.subscriptions.repositories import ISubscriptionRepository
from app.domain.subscriptions.services import ISubscriptionService, SubscriptionService
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import async_session
from app.infrastructure.sqlalchemy.repositories.channels import SAChannelRepository
from app.infrastructure.sqlalchemy.repositories.post_reactions import SAPostReactionRepository
from app.infrastructure.sqlalchemy.repositories.posts import SAPostRepository
from app.infrastructure.sqlalchemy.repositories.subscriptions import SASubscriptionRepository
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

    # Posts
    post_repository = provide(SAPostRepository, provides=IPostRepository)

    # Post reactions
    post_reaction_repository = provide(SAPostReactionRepository, provides=IPostReactionRepository)

    # Subscriptions
    subscription_repository = provide(SASubscriptionRepository, provides=ISubscriptionRepository)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    channel_service = provide(ChannelService, provides=IChannelService)

    # Posts
    post_service = provide(PostService, provides=IPostService)

    # Post reactions
    post_reactions_service = provide(PostReactionService, provides=IPostReactionService)

    # Subscriptions
    subscription_service = provide(SubscriptionService, provides=ISubscriptionService)


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

    # Posts
    create_post = provide(CreatePostUseCase)
    get_post = provide(GetPostUseCase)
    update_post = provide(UpdatePostUseCase)
    delete_post = provide(DeletePostUseCase)

    # Post reactions
    create_post_reaction = provide(CreatePostReactionUseCase)
    delete_post_reaction = provide(DeletePostReactionUseCase)

    # Subscriptions
    subscribe = provide(SubscribeUseCase)
    unsubscribe = provide(UnsubscribeUseCase)
    get_subscribers = provide(GetSubscribersUseCase)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        RepositoriesProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )
