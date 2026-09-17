from collections.abc import AsyncGenerator
from functools import lru_cache

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from types_aiobotocore_s3.client import S3Client

from app.application.auth.use_cases import (
    ActivateChannelUseCase,
    LoginChannelUseCase,
    LogoutUseCase,
    RefreshJWTTokenUseCase,
    RegisterChannelUseCase,
    ResendChannelActivationCodeUseCase,
    ResetChannelPasswordConfirmUseCase,
    ResetChannelPasswordUseCase,
    SetChannelEmailConfirmUseCase,
    SetChannelEmailUseCase,
    SetChannelPasswordUseCase,
)
from app.application.channels.interfaces import IChannelReader
from app.application.channels.use_cases import (
    ConfirmChannelAvatarUploadUseCase,
    DeleteChannelAvatarUseCase,
    DeleteChannelUseCase,
    GenerateChannelAvatarUploadUrlUseCase,
    GetChannelAboutInfoUseCase,
    GetChannelUseCase,
    UpdateChannelUseCase,
)
from app.application.common.interfaces.email import IEmailProvider, IEmailService
from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3 import IS3Provider, IS3Service
from app.application.common.interfaces.security import IAuthCodeService, IAuthService, IJWTService, IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.common.use_cases.email import (
    SendChannelActivationCodeUseCase,
    SendChannelResetPasswordCodeUseCase,
    SendChannelSetEmailCodeUseCase,
)
from app.application.common.use_cases.s3 import AbortMultipartUploadUseCase, DeleteS3ObjectUseCase
from app.application.oauth.interfaces import IOAuthAccountReader, IOAuthProviderFactory, IOAuthServiceFactory
from app.application.oauth.use_cases import (
    OAuthDisconnectAccountUseCase,
    OAuthGetConnectedAccountsUseCase,
    OAuthGetLoginUrlUseCase,
    OAuthVerifyCodeUseCase,
)
from app.application.playlists.interfaces import IPlaylistReader
from app.application.playlists.use_cases import (
    AddVideoToPlaylistUseCase,
    CreatePlaylistUseCase,
    DeletePlaylistUseCase,
    DeleteVideoFromPlaylistUseCase,
    GetChannelPlaylistsUseCase,
    GetPersonalPlaylistsUseCase,
    GetPlaylistUseCase,
    GetPlaylistVideosUseCase,
    UpdatePlaylistUseCase,
)
from app.application.posts.interfaces import IPostCommentReader, IPostReader
from app.application.posts.use_cases import (
    CreatePostCommentReactionUseCase,
    CreatePostCommentUseCase,
    CreatePostReactionUseCase,
    CreatePostUseCase,
    DeletePostCommentReactionUseCase,
    DeletePostCommentUseCase,
    DeletePostReactionUseCase,
    DeletePostUseCase,
    GetPostCommentRepliesUseCase,
    GetPostCommentsUseCase,
    GetPostsUseCase,
    GetPostUseCase,
    UpdatePostCommentUseCase,
    UpdatePostUseCase,
)
from app.application.subscriptions.interfaces import ISubscriptionReader
from app.application.subscriptions.use_cases import (
    GetSubscribersUseCase,
    GetSubscriptionsUseCase,
    SubscribeUseCase,
    UnsubscribeUseCase,
)
from app.application.videos.interfaces import IVideoCommentReader, IVideoHistoryReader, IVideoReader
from app.application.videos.use_cases import (
    AbortVideoMultipartUploadUseCase,
    AddVideoToHistoryUseCase,
    ClearVideoHistoryUseCase,
    CompleteVideoMultipartUploadUseCase,
    ConfirmVideoThumbnailUploadUseCase,
    CreateVideoCommentReactionUseCase,
    CreateVideoCommentUseCase,
    CreateVideoMultipartUploadUseCase,
    CreateVideoReactionUseCase,
    CreateVideoUseCase,
    CreateVideoViewUseCase,
    DeleteNotCompletedVideosUseCase,
    DeleteVideoCommentReactionUseCase,
    DeleteVideoCommentUseCase,
    DeleteVideoFromHistoryUseCase,
    DeleteVideoReactionUseCase,
    DeleteVideoThumbnailUseCase,
    DeleteVideoUseCase,
    GenerateVideoDownloadUrlUseCase,
    GenerateVideoPartUploadUrlUseCase,
    GenerateVideoThumbnailUploadUrlUseCase,
    GetChannelVideosUseCase,
    GetPersonalVideosUseCase,
    GetVideoCommentRepliesUseCase,
    GetVideoCommentsUseCase,
    GetVideoHistoryUseCase,
    GetVideoUseCase,
    UpdateVideoCommentUseCase,
    UpdateVideoUseCase,
)
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
from app.infrastructure.email.service import EmailService
from app.infrastructure.files.file_type_detector import FileTypeDetector
from app.infrastructure.http.base import IHttpClient
from app.infrastructure.http.httpx_client import HttpxClient
from app.infrastructure.http.httpx_config import get_httpx_client
from app.infrastructure.oauth.providers import GitHubOAuthProvider, GoogleOAuthProvider, OAuthProviderFactory
from app.infrastructure.oauth.service import OAuthServiceFactory
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.redis.repo import RedisRepo
from app.infrastructure.s3.config import get_s3_client
from app.infrastructure.s3.provider import BotoS3Provider
from app.infrastructure.s3.service import S3Service
from app.infrastructure.security.auth_code_service import AuthCodeService
from app.infrastructure.security.auth_service import AuthService
from app.infrastructure.security.jwt_service import JWTService
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


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_httpx_async_client(self) -> AsyncGenerator[AsyncClient]:
        client = get_httpx_client()
        yield client
        await client.aclose()

    @provide(scope=Scope.APP)
    async def provide_s3_async_client(self) -> AsyncGenerator[S3Client]:
        async with get_s3_client() as s3_client:
            yield s3_client

    http_client = provide(HttpxClient, scope=Scope.REQUEST, provides=IHttpClient)
    transaction_manager = provide(SATransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
    file_type_detector = provide(FileTypeDetector, scope=Scope.REQUEST, provides=IFileTypeDetector)
    smtp_client = provide(FastMailClient, scope=Scope.APP)
    s3_provider = provide(BotoS3Provider, scope=Scope.REQUEST, provides=IS3Provider)
    s3_service = provide(S3Service, scope=Scope.REQUEST, provides=IS3Service)
    email_provider = provide(FastMailProvider, scope=Scope.REQUEST, provides=IEmailProvider)
    email_service = provide(EmailService, scope=Scope.REQUEST, provides=IEmailService)


class SecurityProvider(Provider):
    password_hasher = provide(PwdlibPasswordHasher, scope=Scope.APP, provides=IPasswordHasher)
    jwt_service = provide(JWTService, scope=Scope.APP, provides=IJWTService)
    auth_service = provide(AuthService, scope=Scope.REQUEST, provides=IAuthService)
    auth_code_service = provide(AuthCodeService, scope=Scope.REQUEST, provides=IAuthCodeService)


class OAuthProvider(Provider):
    scope = Scope.REQUEST

    @provide(provides=IOAuthProviderFactory)
    def provide_oauth_provider_factory(
        self,
        github_provider: GitHubOAuthProvider,
        google_provider: GoogleOAuthProvider,
    ) -> IOAuthProviderFactory:
        return OAuthProviderFactory(
            providers=[
                github_provider,
                google_provider,
            ]
        )

    github_oauth_provider = provide(GitHubOAuthProvider)
    google_oauth_provider = provide(GoogleOAuthProvider)
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
    refresh_jwt_token = provide(RefreshJWTTokenUseCase)
    logout = provide(LogoutUseCase)
    activate_channel = provide(ActivateChannelUseCase)
    resend_channel_activation_code = provide(ResendChannelActivationCodeUseCase)
    set_channel_email = provide(SetChannelEmailUseCase)
    set_channel_email_confirm = provide(SetChannelEmailConfirmUseCase)
    set_channel_password = provide(SetChannelPasswordUseCase)
    reset_channel_password = provide(ResetChannelPasswordUseCase)
    reset_channel_password_confirm = provide(ResetChannelPasswordConfirmUseCase)

    # OAuth
    get_login_url = provide(OAuthGetLoginUrlUseCase)
    verify_code = provide(OAuthVerifyCodeUseCase)
    get_connected_accounts = provide(OAuthGetConnectedAccountsUseCase)
    disconnect_account = provide(OAuthDisconnectAccountUseCase)

    # Videos
    create_video = provide(CreateVideoUseCase)
    delete_video = provide(DeleteVideoUseCase)
    update_video = provide(UpdateVideoUseCase)
    get_video = provide(GetVideoUseCase)
    get_personal_videos = provide(GetPersonalVideosUseCase)
    get_channel_videos = provide(GetChannelVideosUseCase)

    generate_video_thumbnail_upload_url = provide(GenerateVideoThumbnailUploadUrlUseCase)
    confirm_video_thumbnail_upload = provide(ConfirmVideoThumbnailUploadUseCase)
    delete_video_thumbnail = provide(DeleteVideoThumbnailUseCase)

    create_video_multipart_upload = provide(CreateVideoMultipartUploadUseCase)
    abort_video_multipart_upload = provide(AbortVideoMultipartUploadUseCase)
    generate_video_part_upload_url = provide(GenerateVideoPartUploadUrlUseCase)
    complete_video_multipart_upload = provide(CompleteVideoMultipartUploadUseCase)
    generate_video_download_url = provide(GenerateVideoDownloadUrlUseCase)

    delete_not_completed_videos = provide(DeleteNotCompletedVideosUseCase)

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
        SecurityProvider(),
        OAuthProvider(),
        DatabaseProvider(),
        ReposProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )
