from dishka import Provider, Scope, provide

from app.application.common.interfaces.security import IAuthCodeService, IAuthService, IJWTService
from app.domain.channels.services import ChannelService, IChannelService
from app.domain.playlists.services import IPlaylistItemService, IPlaylistService, PlaylistItemService, PlaylistService
from app.domain.posts.services import (
    IPostCommentReactionService,
    IPostCommentService,
    IPostReactionService,
    IPostService,
    PostCommentReactionService,
    PostCommentService,
    PostReactionService,
    PostService,
)
from app.domain.subscriptions.services import ISubscriptionService, SubscriptionService
from app.domain.videos.services import (
    IVideoCommentReactionService,
    IVideoCommentService,
    IVideoHistoryService,
    IVideoReactionService,
    IVideoService,
    IVideoViewService,
    VideoCommentReactionService,
    VideoCommentService,
    VideoHistoryService,
    VideoReactionService,
    VideoService,
    VideoViewService,
)
from app.infrastructure.security.auth_code_service import AuthCodeService
from app.infrastructure.security.auth_service import AuthService
from app.infrastructure.security.jwt_service import JWTService


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

    jwt_service = provide(JWTService, scope=Scope.APP, provides=IJWTService)
    auth_service = provide(AuthService, scope=Scope.REQUEST, provides=IAuthService)
    auth_code_service = provide(AuthCodeService, scope=Scope.REQUEST, provides=IAuthCodeService)
