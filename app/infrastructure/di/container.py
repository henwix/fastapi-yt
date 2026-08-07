from collections.abc import AsyncGenerator
from functools import lru_cache

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.auth.use_cases.login import LoginUseCase
from app.application.channels.use_cases.confirm_channel_avatar_upload import ConfirmChannelAvatarUploadUseCase
from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.application.channels.use_cases.delete_channel_avatar import DeleteChannelAvatarUseCase
from app.application.channels.use_cases.generate_channel_avatar_upload_url import GenerateChannelAvatarUploadUrlUseCase
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.application.channels.use_cases.set_channel_password import SetChannelPasswordUseCase
from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
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
from app.application.videos.use_cases.get_personal_videos import GetPersonalVideosUseCase
from app.application.videos.use_cases.get_video import GetVideoUseCase
from app.application.videos.use_cases.update_video import UpdateVideoUseCase
from app.domain.channels.repositories import IChannelRepository
from app.domain.channels.services import ChannelService, IChannelService
from app.domain.playlists.repositories import IPlaylistItemRepository, IPlaylistRepository
from app.domain.playlists.services import IPlaylistItemService, IPlaylistService, PlaylistItemService, PlaylistService
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
from app.domain.video_comments.repositories import IVideoCommentRepository
from app.domain.video_comments.services import IVideoCommentService, VideoCommentService
from app.domain.video_history.repositories import IVideoHistoryRepository
from app.domain.video_history.services import IVideoHistoryService, VideoHistoryService
from app.domain.video_reactions.repositories import IVideoReactionRepository
from app.domain.video_reactions.services import IVideoReactionService, VideoReactionService
from app.domain.video_views.repositories import IVideoViewRepository
from app.domain.video_views.services import IVideoViewService, VideoViewService
from app.domain.videos.repositories import IVideoRepository
from app.domain.videos.services import IVideoService, VideoService
from app.infrastructure.s3.client import BotoS3Client
from app.infrastructure.s3.provider import BotoS3Provider
from app.infrastructure.security.jwt import JWTService
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.readers.playlists import SAPlaylistReader
from app.infrastructure.sqlalchemy.readers.post_comments import SAPostCommentReader
from app.infrastructure.sqlalchemy.readers.posts import SAPostReader
from app.infrastructure.sqlalchemy.readers.subscriptions import SASubscriptionReader
from app.infrastructure.sqlalchemy.readers.video_comments import SAVideoCommentReader
from app.infrastructure.sqlalchemy.readers.video_history import SAVideoHistoryReader
from app.infrastructure.sqlalchemy.readers.videos import SAVideoReader
from app.infrastructure.sqlalchemy.repositories.channels import SAChannelRepository
from app.infrastructure.sqlalchemy.repositories.playlists import SAPlaylistItemRepository, SAPlaylistRepository
from app.infrastructure.sqlalchemy.repositories.post_comment_reactions import SAPostCommentReactionRepository
from app.infrastructure.sqlalchemy.repositories.post_comments import SAPostCommentRepository
from app.infrastructure.sqlalchemy.repositories.post_reactions import SAPostReactionRepository
from app.infrastructure.sqlalchemy.repositories.posts import SAPostRepository
from app.infrastructure.sqlalchemy.repositories.subscriptions import SASubscriptionRepository
from app.infrastructure.sqlalchemy.repositories.video_comments import SAVideoCommentRepository
from app.infrastructure.sqlalchemy.repositories.video_history import SAVideoHistoryRepository
from app.infrastructure.sqlalchemy.repositories.video_reactions import SAVideoReactionRepository
from app.infrastructure.sqlalchemy.repositories.video_views import SAVideoViewRepository
from app.infrastructure.sqlalchemy.repositories.videos import SAVideoRepository
from app.infrastructure.sqlalchemy.transaction_manager import SATransactionManager
from app.infrastructure.taskiq.task_queue import TaskiqTaskQueue


class AppProvider(Provider):
    transaction_manager = provide(SATransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
    password_hasher = provide(PwdlibPasswordHasher, scope=Scope.APP, provides=IPasswordHasher)
    jwt_service = provide(JWTService, scope=Scope.APP, provides=IJWTService)
    s3_client = provide(BotoS3Client, scope=Scope.APP)
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

    channel_repository = provide(SAChannelRepository, provides=IChannelRepository)
    video_repository = provide(SAVideoRepository, provides=IVideoRepository)
    video_reaction_repository = provide(SAVideoReactionRepository, provides=IVideoReactionRepository)
    video_history_repository = provide(SAVideoHistoryRepository, provides=IVideoHistoryRepository)
    video_view_repository = provide(SAVideoViewRepository, provides=IVideoViewRepository)
    video_comment_repository = provide(SAVideoCommentRepository, provides=IVideoCommentRepository)
    playlist_repository = provide(SAPlaylistRepository, provides=IPlaylistRepository)
    playlist_item_repository = provide(SAPlaylistItemRepository, provides=IPlaylistItemRepository)
    post_repository = provide(SAPostRepository, provides=IPostRepository)
    post_reaction_repository = provide(SAPostReactionRepository, provides=IPostReactionRepository)
    post_comment_repository = provide(SAPostCommentRepository, provides=IPostCommentRepository)
    post_comment_reaction_repository = provide(SAPostCommentReactionRepository, provides=IPostCommentReactionRepository)
    subscription_repository = provide(SASubscriptionRepository, provides=ISubscriptionRepository)


class ReadersProvider(Provider):
    scope = Scope.REQUEST

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
    create_channel = provide(CreateChannelUseCase)
    get_channel = provide(GetChannelUseCase)
    update_channel = provide(UpdateChannelUseCase)
    delete_channel = provide(DeleteChannelUseCase)
    set_channel_password = provide(SetChannelPasswordUseCase)
    generate_channel_avatar_upload_url = provide(GenerateChannelAvatarUploadUrlUseCase)
    confirm_channel_avatar_upload = provide(ConfirmChannelAvatarUploadUseCase)
    delete_channel_avatar = provide(DeleteChannelAvatarUseCase)

    # Auth
    login = provide(LoginUseCase)

    # Videos
    delete_video = provide(DeleteVideoUseCase)
    update_video = provide(UpdateVideoUseCase)
    get_video = provide(GetVideoUseCase)
    get_personal_videos = provide(GetPersonalVideosUseCase)

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
