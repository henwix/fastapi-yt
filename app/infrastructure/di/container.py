from collections.abc import AsyncGenerator
from functools import lru_cache

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.auth.use_cases.login import LoginUseCase
from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.application.channels.use_cases.set_password import SetChannelPasswordUseCase
from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comments.interfaces.reader import IPostCommentReader
from app.application.post_comments.use_cases.create_post_comment import CreatePostCommentUseCase
from app.application.post_comments.use_cases.delete_post_comment import DeletePostCommentUseCase
from app.application.post_comments.use_cases.get_post_comments import GetPostCommentsUseCase
from app.application.post_comments.use_cases.update_post_comment import UpdatePostCommentUseCase
from app.application.post_reactions.use_cases.create_post_reaction import CreatePostReactionUseCase
from app.application.post_reactions.use_cases.delete_post_reaction import DeletePostReactionUseCase
from app.application.posts.use_cases.create_post import CreatePostUseCase
from app.application.posts.use_cases.delete_post import DeletePostUseCase
from app.application.posts.use_cases.get_post import GetPostUseCase
from app.application.posts.use_cases.update_post import UpdatePostUseCase
from app.application.subscriptions.interfaces.reader import ISubscriptionReader
from app.application.subscriptions.use_cases.get_subscribers import GetSubscribersUseCase
from app.application.subscriptions.use_cases.get_subscriptions import GetSubscriptionsUseCase
from app.application.subscriptions.use_cases.subscribe import SubscribeUseCase
from app.application.subscriptions.use_cases.unsubscribe import UnsubscribeUseCase
from app.domain.channels.repositories import IChannelRepository
from app.domain.channels.services import ChannelService, IChannelService
from app.domain.post_comments.repositories import IPostCommentRepository
from app.domain.post_comments.services import IPostCommentService, PostCommentService
from app.domain.post_reactions.repositories import IPostReactionRepository
from app.domain.post_reactions.services import IPostReactionService, PostReactionService
from app.domain.posts.repositories import IPostRepository
from app.domain.posts.services import IPostService, PostService
from app.domain.subscriptions.repositories import ISubscriptionRepository
from app.domain.subscriptions.services import ISubscriptionService, SubscriptionService
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import async_session
from app.infrastructure.sqlalchemy.readers.post_comments import SAPostCommentReader
from app.infrastructure.sqlalchemy.readers.subscriptions import SASubscriptionReader
from app.infrastructure.sqlalchemy.repositories.channels import SAChannelRepository
from app.infrastructure.sqlalchemy.repositories.post_comments import SAPostCommentRepository
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

    # Post comments
    post_comment_repository = provide(SAPostCommentRepository, provides=IPostCommentRepository)

    # Subscriptions
    subscription_repository = provide(SASubscriptionRepository, provides=ISubscriptionRepository)


class ReadersProvider(Provider):
    scope = Scope.REQUEST

    # Post comments
    post_comment_reader = provide(SAPostCommentReader, provides=IPostCommentReader)

    # Subscriptions
    subscriptions_reader = provide(SASubscriptionReader, provides=ISubscriptionReader)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    channel_service = provide(ChannelService, provides=IChannelService)

    # Posts
    post_service = provide(PostService, provides=IPostService)

    # Post reactions
    post_reaction_service = provide(PostReactionService, provides=IPostReactionService)

    # Post comments
    post_comment_service = provide(PostCommentService, provides=IPostCommentService)

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

    # Post comments
    create_post_comment = provide(CreatePostCommentUseCase)
    delete_post_comment = provide(DeletePostCommentUseCase)
    update_post_comment = provide(UpdatePostCommentUseCase)
    get_post_comments = provide(GetPostCommentsUseCase)

    # Subscriptions
    subscribe = provide(SubscribeUseCase)
    unsubscribe = provide(UnsubscribeUseCase)
    get_subscribers = provide(GetSubscribersUseCase)
    get_subscriptions = provide(GetSubscriptionsUseCase)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        RepositoriesProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )
