from collections.abc import AsyncGenerator
from functools import lru_cache

from aioboto3 import Session
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.auth.use_cases.login import LoginUseCase
from app.application.channels.use_cases.confirm_channel_avatar_upload import ConfirmChannelAvatarUploadUseCase
from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.application.channels.use_cases.delete_channel_avatar import DeleteChannelAvatarUseCase
from app.application.channels.use_cases.generate_channel_avatar_upload_url import GenerateChannelAvatarUploadURLUseCase
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.application.channels.use_cases.set_password import SetChannelPasswordUseCase
from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.s3_client import IS3Client
from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comment_reactions.use_cases.create_post_comment_reaction import (
    CreatePostCommentReactionUseCase,
)
from app.application.post_comment_reactions.use_cases.delete_post_comment_reaction import (
    DeletePostCommentReactionUseCase,
)
from app.application.post_comments.interfaces.reader import IPostCommentReader
from app.application.post_comments.use_cases.create_post_comment import CreatePostCommentUseCase
from app.application.post_comments.use_cases.delete_post_comment import DeletePostCommentUseCase
from app.application.post_comments.use_cases.get_post_comment_replies import GetPostCommentRepliesUseCase
from app.application.post_comments.use_cases.get_post_comments import GetPostCommentsUseCase
from app.application.post_comments.use_cases.update_post_comment import UpdatePostCommentUseCase
from app.application.post_reactions.use_cases.create_post_reaction import CreatePostReactionUseCase
from app.application.post_reactions.use_cases.delete_post_reaction import DeletePostReactionUseCase
from app.application.posts.interfaces.reader import IPostReader
from app.application.posts.use_cases.create_post import CreatePostUseCase
from app.application.posts.use_cases.delete_post import DeletePostUseCase
from app.application.posts.use_cases.get_post import GetPostUseCase
from app.application.posts.use_cases.get_posts import GetPostsUseCase
from app.application.posts.use_cases.update_post import UpdatePostUseCase
from app.application.subscriptions.interfaces.reader import ISubscriptionReader
from app.application.subscriptions.use_cases.get_subscribers import GetSubscribersUseCase
from app.application.subscriptions.use_cases.get_subscriptions import GetSubscriptionsUseCase
from app.application.subscriptions.use_cases.subscribe import SubscribeUseCase
from app.application.subscriptions.use_cases.unsubscribe import UnsubscribeUseCase
from app.domain.channels.repositories import IChannelRepository
from app.domain.channels.services import ChannelService, IChannelService
from app.domain.post_comment_reactions.repositories import IPostCommentReactionRepository
from app.domain.post_comment_reactions.services import IPostCommentReactionService, PostCommentReactionService
from app.domain.post_comments.repositories import IPostCommentRepository
from app.domain.post_comments.services import IPostCommentService, PostCommentService
from app.domain.post_reactions.repositories import IPostReactionRepository
from app.domain.post_reactions.services import IPostReactionService, PostReactionService
from app.domain.posts.repositories import IPostRepository
from app.domain.posts.services import IPostService, PostService
from app.domain.subscriptions.repositories import ISubscriptionRepository
from app.domain.subscriptions.services import ISubscriptionService, SubscriptionService
from app.infrastructure.s3.client import BotoS3Client
from app.infrastructure.s3.provider import BotoS3Provider
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.readers.post_comments import SAPostCommentReader
from app.infrastructure.sqlalchemy.readers.posts import SAPostReader
from app.infrastructure.sqlalchemy.readers.subscriptions import SASubscriptionReader
from app.infrastructure.sqlalchemy.repositories.channels import SAChannelRepository
from app.infrastructure.sqlalchemy.repositories.post_comment_reactions import SAPostCommentReactionRepository
from app.infrastructure.sqlalchemy.repositories.post_comments import SAPostCommentRepository
from app.infrastructure.sqlalchemy.repositories.post_reactions import SAPostReactionRepository
from app.infrastructure.sqlalchemy.repositories.posts import SAPostRepository
from app.infrastructure.sqlalchemy.repositories.subscriptions import SASubscriptionRepository
from app.infrastructure.sqlalchemy.transaction_manager import SATransactionManager
from app.infrastructure.taskiq.task_queue import TaskiqTaskQueue


class AppProvider(Provider):
    @provide(scope=Scope.APP, provides=Session)
    def provide_boto_session(self) -> Session:
        return Session()

    transaction_manager = provide(SATransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
    password_hasher = provide(PwdlibPasswordHasher, scope=Scope.APP, provides=IPasswordHasher)
    jwt_service = provide(JWTService, scope=Scope.APP, provides=IJWTService)
    s3_client = provide(BotoS3Client, scope=Scope.APP, provides=IS3Client)
    s3_provider = provide(BotoS3Provider, scope=Scope.REQUEST, provides=IS3Provider)
    task_queue = provide(TaskiqTaskQueue, scope=Scope.REQUEST, provides=ITaskQueue)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncEngine)
    async def engine(self) -> AsyncGenerator[AsyncEngine]:
        engine = create_engine()
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP, provides=async_sessionmaker)
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
        return create_session_factory(engine=engine)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_async_session(self, session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession]:
        session = session_factory()
        yield session
        await session.close()


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

    # Post comment reactions
    post_comment_reaction_repository = provide(SAPostCommentReactionRepository, provides=IPostCommentReactionRepository)

    # Subscriptions
    subscription_repository = provide(SASubscriptionRepository, provides=ISubscriptionRepository)


class ReadersProvider(Provider):
    scope = Scope.REQUEST

    # Posts
    post_reader = provide(SAPostReader, provides=IPostReader)

    # Post comments
    post_comment_reader = provide(SAPostCommentReader, provides=IPostCommentReader)

    # Subscriptions
    subscription_reader = provide(SASubscriptionReader, provides=ISubscriptionReader)


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

    # Post comment reactions
    post_comment_reaction_service = provide(PostCommentReactionService, provides=IPostCommentReactionService)

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
    generate_channel_avatar_upload_url = provide(GenerateChannelAvatarUploadURLUseCase)
    confirm_channel_avatar_upload = provide(ConfirmChannelAvatarUploadUseCase)
    delete_channel_avatar = provide(DeleteChannelAvatarUseCase)

    # Auth
    login = provide(LoginUseCase)

    # Posts
    create_post = provide(CreatePostUseCase)
    get_post = provide(GetPostUseCase)
    get_posts = provide(GetPostsUseCase)
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
    get_post_comment_replies = provide(GetPostCommentRepliesUseCase)

    # Post comment reactions
    create_post_comment_reaction = provide(CreatePostCommentReactionUseCase)
    delete_post_comment_reaction = provide(DeletePostCommentReactionUseCase)

    # Subscriptions
    subscribe = provide(SubscribeUseCase)
    unsubscribe = provide(UnsubscribeUseCase)
    get_subscribers = provide(GetSubscribersUseCase)
    get_subscriptions = provide(GetSubscriptionsUseCase)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )
