from collections.abc import AsyncGenerator
from functools import lru_cache

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.auth.use_cases.activate_channel import ActivateChannelUseCase
from app.application.auth.use_cases.login_channel import LoginChannelUseCase
from app.application.auth.use_cases.register_channel import RegisterChannelUseCase
from app.application.auth.use_cases.resend_channel_activation import ResendChannelActivationCodeUseCase
from app.application.auth.use_cases.reset_channel_password import ResetChannelPasswordUseCase
from app.application.auth.use_cases.reset_channel_password_confirm import ResetChannelPasswordConfirmUseCase
from app.application.auth.use_cases.set_channel_email import SetChannelEmailUseCase
from app.application.auth.use_cases.set_channel_email_confirm import SetChannelEmailConfirmUseCase
from app.application.auth.use_cases.set_channel_password import SetChannelPasswordUseCase
from app.application.channels.interfaces.reader import IChannelReader
from app.application.channels.use_cases.confirm_channel_avatar_upload import ConfirmChannelAvatarUploadUseCase
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.application.channels.use_cases.delete_channel_avatar import DeleteChannelAvatarUseCase
from app.application.channels.use_cases.generate_channel_avatar_upload_url import GenerateChannelAvatarUploadUrlUseCase
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.application.channels.use_cases.get_channel_about_info import GetChannelAboutInfoUseCase
from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.application.common.interfaces.email_provider import IEmailProvider
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.task_queues.email import IEmailTaskQueue
from app.application.common.interfaces.task_queues.s3 import IS3TaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.common.use_cases.email.send_channel_activation_code import SendChannelActivationCodeUseCase
from app.application.common.use_cases.email.send_channel_reset_password_code import SendChannelResetPasswordCodeUseCase
from app.application.common.use_cases.email.send_channel_set_email_code import SendChannelSetEmailCodeUseCase
from app.application.common.use_cases.s3.abort_multipart_upload import AbortMultipartUploadUseCase
from app.application.common.use_cases.s3.delete_s3_object import DeleteS3ObjectUseCase
from app.application.oauth.interfaces.provider import IOAuthProviderFactory
from app.application.oauth.interfaces.reader import IOAuthAccountReader
from app.application.oauth.interfaces.service import IOAuthServiceFactory
from app.application.oauth.use_cases.convert_code import OAuthConvertCodeUseCase
from app.application.oauth.use_cases.disconnect_account import OAuthDisconnectAccountUseCase
from app.application.oauth.use_cases.get_connected_accounts import OAuthGetConnectedAccountsUseCase
from app.application.oauth.use_cases.get_login_url import OAuthGetLoginUrlUseCase
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.application.playlists.use_cases.add_video_to_playlist import AddVideoToPlaylistUseCase
from app.application.playlists.use_cases.create_playlist import CreatePlaylistUseCase
from app.application.playlists.use_cases.delete_playlist import DeletePlaylistUseCase
from app.application.playlists.use_cases.delete_video_from_playlist import DeleteVideoFromPlaylistUseCase
from app.application.playlists.use_cases.get_channel_playlists import GetChannelPlaylistsUseCase
from app.application.playlists.use_cases.get_personal_playlists import GetPersonalPlaylistsUseCase
from app.application.playlists.use_cases.get_playlist import GetPlaylistUseCase
from app.application.playlists.use_cases.get_playlist_videos import GetPlaylistVideosUseCase
from app.application.playlists.use_cases.update_playlist import UpdatePlaylistUseCase
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
from app.application.video_comment_reactions.use_cases.create_video_comment_reaction import (
    CreateVideoCommentReactionUseCase,
)
from app.application.video_comment_reactions.use_cases.delete_video_comment_reaction import (
    DeleteVideoCommentReactionUseCase,
)
from app.application.video_comments.interfaces.reader import IVideoCommentReader
from app.application.video_comments.use_cases.create_video_comment import CreateVideoCommentUseCase
from app.application.video_comments.use_cases.delete_video_comment import DeleteVideoCommentUseCase
from app.application.video_comments.use_cases.get_video_comment_replies import GetVideoCommentRepliesUseCase
from app.application.video_comments.use_cases.get_video_comments import GetVideoCommentsUseCase
from app.application.video_comments.use_cases.update_video_comment import UpdateVideoCommentUseCase
from app.application.video_history.interfaces.reader import IVideoHistoryReader
from app.application.video_history.use_cases.add_video_to_history import AddVideoToHistoryUseCase
from app.application.video_history.use_cases.clear_video_history import ClearVideoHistoryUseCase
from app.application.video_history.use_cases.delete_video_from_history import DeleteVideoFromHistoryUseCase
from app.application.video_history.use_cases.get_video_history import GetVideoHistoryUseCase
from app.application.video_reactions.use_cases.create_video_reaction import CreateVideoReactionUseCase
from app.application.video_reactions.use_cases.delete_video_reaction import DeleteVideoReactionUseCase
from app.application.video_views.use_cases.create_video_view import CreateVideoViewUseCase
from app.application.videos.interfaces.reader import IVideoReader
from app.application.videos.use_cases.abort_video_multipart_upload import AbortVideoMultipartUploadUseCase
from app.application.videos.use_cases.complete_video_multipart_upload import CompleteVideoMultipartUploadUseCase
from app.application.videos.use_cases.create_video_multipart_upload import CreateVideoMultipartUploadUseCase
from app.application.videos.use_cases.delete_video import DeleteVideoUseCase
from app.application.videos.use_cases.generate_video_download_url import GenerateVideoDownloadUrlUseCase
from app.application.videos.use_cases.generate_video_part_upload_url import GenerateVideoPartUploadUrlUseCase
from app.application.videos.use_cases.get_channel_videos import GetChannelVideosUseCase
from app.application.videos.use_cases.get_personal_videos import GetPersonalVideosUseCase
from app.application.videos.use_cases.get_video import GetVideoUseCase
from app.application.videos.use_cases.update_video import UpdateVideoUseCase
from app.domain.auth.service import AuthService, IAuthService
from app.domain.channels.repo import IChannelRepo
from app.domain.channels.service import ChannelService, IChannelService
from app.domain.common.repos.kv import IKVRepo
from app.domain.oauth.repo import IOAuthAccountRepo
from app.domain.oauth.service import IOAuthAccountService, OAuthAccountService
from app.domain.playlists.repo import IPlaylistItemRepo, IPlaylistRepo
from app.domain.playlists.service import IPlaylistItemService, IPlaylistService, PlaylistItemService, PlaylistService
from app.domain.post_comment_reactions.repo import IPostCommentReactionRepo
from app.domain.post_comment_reactions.service import IPostCommentReactionService, PostCommentReactionService
from app.domain.post_comments.repo import IPostCommentRepo
from app.domain.post_comments.service import IPostCommentService, PostCommentService
from app.domain.post_reactions.repo import IPostReactionRepo
from app.domain.post_reactions.service import IPostReactionService, PostReactionService
from app.domain.posts.repo import IPostRepo
from app.domain.posts.service import IPostService, PostService
from app.domain.subscriptions.repo import ISubscriptionRepo
from app.domain.subscriptions.service import ISubscriptionService, SubscriptionService
from app.domain.video_comment_reactions.repo import IVideoCommentReactionRepo
from app.domain.video_comment_reactions.service import IVideoCommentReactionService, VideoCommentReactionService
from app.domain.video_comments.repo import IVideoCommentRepo
from app.domain.video_comments.service import IVideoCommentService, VideoCommentService
from app.domain.video_history.repo import IVideoHistoryRepo
from app.domain.video_history.service import IVideoHistoryService, VideoHistoryService
from app.domain.video_reactions.repo import IVideoReactionRepo
from app.domain.video_reactions.service import IVideoReactionService, VideoReactionService
from app.domain.video_views.repo import IVideoViewRepo
from app.domain.video_views.service import IVideoViewService, VideoViewService
from app.domain.videos.repo import IVideoRepo
from app.domain.videos.service import IVideoService, VideoService
from app.infrastructure.email.client import FastMailClient
from app.infrastructure.email.provider import FastMailProvider
from app.infrastructure.http.base import IHttpClient
from app.infrastructure.http.httpx_client import HttpxHttpClient
from app.infrastructure.http.httpx_config import get_httpx_client
from app.infrastructure.oauth.providers.factory import OAuthProviderFactory
from app.infrastructure.oauth.providers.github import GitHubOAuthProvider
from app.infrastructure.oauth.service import OAuthServiceFactory
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.redis.repo import RedisRepo
from app.infrastructure.s3.client import BotoS3Client
from app.infrastructure.s3.provider import BotoS3Provider
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.readers.channels import SAChannelReader
from app.infrastructure.sqlalchemy.readers.oauth import SAOAuthAccountReader
from app.infrastructure.sqlalchemy.readers.playlists import SAPlaylistReader
from app.infrastructure.sqlalchemy.readers.post_comments import SAPostCommentReader
from app.infrastructure.sqlalchemy.readers.posts import SAPostReader
from app.infrastructure.sqlalchemy.readers.subscriptions import SASubscriptionReader
from app.infrastructure.sqlalchemy.readers.video_comments import SAVideoCommentReader
from app.infrastructure.sqlalchemy.readers.video_history import SAVideoHistoryReader
from app.infrastructure.sqlalchemy.readers.videos import SAVideoReader
from app.infrastructure.sqlalchemy.repos.channels import SAChannelRepo
from app.infrastructure.sqlalchemy.repos.oauth import SAOAuthAccountRepo
from app.infrastructure.sqlalchemy.repos.playlists import SAPlaylistItemRepo, SAPlaylistRepo
from app.infrastructure.sqlalchemy.repos.post_comment_reactions import SAPostCommentReactionRepo
from app.infrastructure.sqlalchemy.repos.post_comments import SAPostCommentRepo
from app.infrastructure.sqlalchemy.repos.post_reactions import SAPostReactionRepo
from app.infrastructure.sqlalchemy.repos.posts import SAPostRepo
from app.infrastructure.sqlalchemy.repos.subscriptions import SASubscriptionRepo
from app.infrastructure.sqlalchemy.repos.video_comment_reactions import SAVideoCommentReactionRepo
from app.infrastructure.sqlalchemy.repos.video_comments import SAVideoCommentRepo
from app.infrastructure.sqlalchemy.repos.video_history import SAVideoHistoryRepo
from app.infrastructure.sqlalchemy.repos.video_reactions import SAVideoReactionRepo
from app.infrastructure.sqlalchemy.repos.video_views import SAVideoViewRepo
from app.infrastructure.sqlalchemy.repos.videos import SAVideoRepo
from app.infrastructure.sqlalchemy.transaction_manager import SATransactionManager
from app.infrastructure.taskiq.task_queues.email import TaskiqEmailTaskQueue
from app.infrastructure.taskiq.task_queues.s3 import TaskiqS3TaskQueue


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_httpx_async_client(self) -> AsyncGenerator[AsyncClient]:
        client = get_httpx_client()
        yield client
        await client.aclose()

    http_client = provide(HttpxHttpClient, scope=Scope.REQUEST, provides=IHttpClient)
    transaction_manager = provide(SATransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
    password_hasher = provide(PwdlibPasswordHasher, scope=Scope.APP, provides=IPasswordHasher)
    jwt_service = provide(JWTService, scope=Scope.APP, provides=IJWTService)
    s3_client = provide(BotoS3Client, scope=Scope.APP)
    smtp_client = provide(FastMailClient, scope=Scope.APP)
    s3_provider = provide(BotoS3Provider, scope=Scope.REQUEST, provides=IS3Provider)
    email_provider = provide(FastMailProvider, scope=Scope.REQUEST, provides=IEmailProvider)
    s3_task_queue = provide(TaskiqS3TaskQueue, scope=Scope.REQUEST, provides=IS3TaskQueue)
    email_task_queue = provide(TaskiqEmailTaskQueue, scope=Scope.REQUEST, provides=IEmailTaskQueue)


class OAuthProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=IOAuthProviderFactory)
    def provide_oauth_provider_factory(
        self,
        github_provider: GitHubOAuthProvider,
    ) -> IOAuthProviderFactory:
        return OAuthProviderFactory(
            providers=[
                github_provider,
            ]
        )

    github_oauth_provider = provide(GitHubOAuthProvider)
    oauth_service_factory = provide(OAuthServiceFactory, provides=IOAuthServiceFactory)
    oauth_account_service = provide(OAuthAccountService, provides=IOAuthAccountService)


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

    @provide(scope=Scope.APP)
    async def provide_redis_client(self) -> AsyncGenerator[Redis]:
        redis = get_redis_client()
        yield redis
        await redis.aclose()


class ReposProvider(Provider):
    scope = Scope.REQUEST

    redis_repo = provide(RedisRepo, provides=IKVRepo)

    oauth_repo = provide(SAOAuthAccountRepo, provides=IOAuthAccountRepo)
    channel_repo = provide(SAChannelRepo, provides=IChannelRepo)
    video_repo = provide(SAVideoRepo, provides=IVideoRepo)
    video_reaction_repo = provide(SAVideoReactionRepo, provides=IVideoReactionRepo)
    video_history_repo = provide(SAVideoHistoryRepo, provides=IVideoHistoryRepo)
    video_view_repo = provide(SAVideoViewRepo, provides=IVideoViewRepo)
    video_comment_repo = provide(SAVideoCommentRepo, provides=IVideoCommentRepo)
    video_comment_reaction_repo = provide(SAVideoCommentReactionRepo, provides=IVideoCommentReactionRepo)
    playlist_repo = provide(SAPlaylistRepo, provides=IPlaylistRepo)
    playlist_item_repo = provide(SAPlaylistItemRepo, provides=IPlaylistItemRepo)
    post_repo = provide(SAPostRepo, provides=IPostRepo)
    post_reaction_repo = provide(SAPostReactionRepo, provides=IPostReactionRepo)
    post_comment_repo = provide(SAPostCommentRepo, provides=IPostCommentRepo)
    post_comment_reaction_repo = provide(SAPostCommentReactionRepo, provides=IPostCommentReactionRepo)
    subscription_repo = provide(SASubscriptionRepo, provides=ISubscriptionRepo)


class ReadersProvider(Provider):
    scope = Scope.REQUEST

    channel_reader = provide(SAChannelReader, provides=IChannelReader)
    oauth_account_reader = provide(SAOAuthAccountReader, provides=IOAuthAccountReader)
    post_reader = provide(SAPostReader, provides=IPostReader)
    post_comment_reader = provide(SAPostCommentReader, provides=IPostCommentReader)
    subscription_reader = provide(SASubscriptionReader, provides=ISubscriptionReader)
    video_reader = provide(SAVideoReader, provides=IVideoReader)
    video_comment_reader = provide(SAVideoCommentReader, provides=IVideoCommentReader)
    video_history_reader = provide(SAVideoHistoryReader, provides=IVideoHistoryReader)
    playlist_reader = provide(SAPlaylistReader, provides=IPlaylistReader)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    auth_service = provide(AuthService, provides=IAuthService)
    channel_service = provide(ChannelService, provides=IChannelService)
    video_service = provide(VideoService, provides=IVideoService)
    video_view_service = provide(VideoViewService, provides=IVideoViewService)
    video_reaction_service = provide(VideoReactionService, provides=IVideoReactionService)
    video_history_service = provide(VideoHistoryService, provides=IVideoHistoryService)
    video_comment_service = provide(VideoCommentService, provides=IVideoCommentService)
    video_comment_reaction_service = provide(VideoCommentReactionService, provides=IVideoCommentReactionService)
    playlist_service = provide(PlaylistService, provides=IPlaylistService)
    playlist_item_service = provide(PlaylistItemService, provides=IPlaylistItemService)
    post_service = provide(PostService, provides=IPostService)
    post_reaction_service = provide(PostReactionService, provides=IPostReactionService)
    post_comment_service = provide(PostCommentService, provides=IPostCommentService)
    post_comment_reaction_service = provide(PostCommentReactionService, provides=IPostCommentReactionService)
    subscription_service = provide(SubscriptionService, provides=ISubscriptionService)


class UseCasesProvider(Provider):
    scope = Scope.REQUEST

    # Channels
    get_channel = provide(GetChannelUseCase)
    get_channel_about_info = provide(GetChannelAboutInfoUseCase)
    update_channel = provide(UpdateChannelUseCase)
    delete_channel = provide(DeleteChannelUseCase)
    generate_channel_avatar_upload_url = provide(GenerateChannelAvatarUploadUrlUseCase)
    confirm_channel_avatar_upload = provide(ConfirmChannelAvatarUploadUseCase)
    delete_channel_avatar = provide(DeleteChannelAvatarUseCase)

    # Auth
    register_channel = provide(RegisterChannelUseCase)
    login_channel = provide(LoginChannelUseCase)
    activate_channel = provide(ActivateChannelUseCase)
    resend_channel_activation_code = provide(ResendChannelActivationCodeUseCase)
    set_channel_email = provide(SetChannelEmailUseCase)
    set_channel_email_confirm = provide(SetChannelEmailConfirmUseCase)
    set_channel_password = provide(SetChannelPasswordUseCase)
    reset_channel_password = provide(ResetChannelPasswordUseCase)
    reset_channel_password_confirm = provide(ResetChannelPasswordConfirmUseCase)

    # OAuth
    get_login_url = provide(OAuthGetLoginUrlUseCase)
    convert_code = provide(OAuthConvertCodeUseCase)
    get_connected_accounts = provide(OAuthGetConnectedAccountsUseCase)
    disconnect_account = provide(OAuthDisconnectAccountUseCase)

    # Videos
    delete_video = provide(DeleteVideoUseCase)
    update_video = provide(UpdateVideoUseCase)
    get_video = provide(GetVideoUseCase)
    get_personal_videos = provide(GetPersonalVideosUseCase)
    get_channel_videos = provide(GetChannelVideosUseCase)

    create_video_multipart_upload = provide(CreateVideoMultipartUploadUseCase)
    abort_video_multipart_upload = provide(AbortVideoMultipartUploadUseCase)
    generate_video_part_upload_url = provide(GenerateVideoPartUploadUrlUseCase)
    complete_video_multipart_upload = provide(CompleteVideoMultipartUploadUseCase)
    generate_video_download_url = provide(GenerateVideoDownloadUrlUseCase)

    # Video views
    create_video_view = provide(CreateVideoViewUseCase)

    # Video reactions
    create_video_reaction = provide(CreateVideoReactionUseCase)
    delete_video_reaction = provide(DeleteVideoReactionUseCase)

    # Video comment reactions
    create_video_comment_reaction = provide(CreateVideoCommentReactionUseCase)
    delete_video_comment_reaction = provide(DeleteVideoCommentReactionUseCase)

    # Video comments
    create_video_comment = provide(CreateVideoCommentUseCase)
    delete_video_comment = provide(DeleteVideoCommentUseCase)
    update_video_comment = provide(UpdateVideoCommentUseCase)
    get_video_comments = provide(GetVideoCommentsUseCase)
    get_video_comment_replies = provide(GetVideoCommentRepliesUseCase)

    # Video history
    add_video_to_history = provide(AddVideoToHistoryUseCase)
    delete_video_from_history = provide(DeleteVideoFromHistoryUseCase)
    clear_video_history = provide(ClearVideoHistoryUseCase)
    get_video_history = provide(GetVideoHistoryUseCase)

    # Playlists
    create_playlist = provide(CreatePlaylistUseCase)
    get_playlist = provide(GetPlaylistUseCase)
    get_playlist_videos = provide(GetPlaylistVideosUseCase)
    get_personal_playlists = provide(GetPersonalPlaylistsUseCase)
    get_channel_playlists = provide(GetChannelPlaylistsUseCase)
    delete_playlist = provide(DeletePlaylistUseCase)
    update_playlist = provide(UpdatePlaylistUseCase)
    add_video_to_playlist = provide(AddVideoToPlaylistUseCase)
    delete_video_from_playlist = provide(DeleteVideoFromPlaylistUseCase)

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

    # Common/Email
    send_channel_activation_code = provide(SendChannelActivationCodeUseCase)
    send_channel_set_email_code = provide(SendChannelSetEmailCodeUseCase)
    send_channel_reset_password_code = provide(SendChannelResetPasswordCodeUseCase)

    # Common/S3
    delete_s3_object = provide(DeleteS3ObjectUseCase)
    abort_multipart_upload = provide(AbortMultipartUploadUseCase)


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(
        AppProvider(),
        OAuthProvider(),
        DatabaseProvider(),
        ReposProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )
