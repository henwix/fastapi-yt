from dishka import Provider, Scope, provide

from app.domain.channels.repos import IChannelRepo
from app.domain.common.repos.kv import IKVRepo
from app.domain.oauth.repos import IOAuthAccountRepo
from app.domain.playlists.repos import IPlaylistItemRepo, IPlaylistRepo
from app.domain.posts.repos import IPostCommentReactionRepo, IPostCommentRepo, IPostReactionRepo, IPostRepo
from app.domain.subscriptions.repos import ISubscriptionRepo
from app.domain.videos.repos import (
    IVideoCommentReactionRepo,
    IVideoCommentRepo,
    IVideoHistoryRepo,
    IVideoReactionRepo,
    IVideoRepo,
    IVideoViewRepo,
)
from app.infrastructure.redis.repo import RedisRepo
from app.infrastructure.sqlalchemy.repos import (
    ChannelRepo,
    OAuthAccountRepo,
    PlaylistItemRepo,
    PlaylistRepo,
    PostCommentReactionRepo,
    PostCommentRepo,
    PostReactionRepo,
    PostRepo,
    SubscriptionRepo,
    VideoCommentReactionRepo,
    VideoCommentRepo,
    VideoHistoryRepo,
    VideoReactionRepo,
    VideoRepo,
    VideoViewRepo,
)


class ReposProvider(Provider):
    scope = Scope.REQUEST

    redis_repo = provide(RedisRepo, provides=IKVRepo)

    oauth_repo = provide(OAuthAccountRepo, provides=IOAuthAccountRepo)
    channel_repo = provide(ChannelRepo, provides=IChannelRepo)
    video_repo = provide(VideoRepo, provides=IVideoRepo)
    video_reaction_repo = provide(VideoReactionRepo, provides=IVideoReactionRepo)
    video_history_repo = provide(VideoHistoryRepo, provides=IVideoHistoryRepo)
    video_view_repo = provide(VideoViewRepo, provides=IVideoViewRepo)
    video_comment_repo = provide(VideoCommentRepo, provides=IVideoCommentRepo)
    video_comment_reaction_repo = provide(VideoCommentReactionRepo, provides=IVideoCommentReactionRepo)
    playlist_repo = provide(PlaylistRepo, provides=IPlaylistRepo)
    playlist_item_repo = provide(PlaylistItemRepo, provides=IPlaylistItemRepo)
    post_repo = provide(PostRepo, provides=IPostRepo)
    post_reaction_repo = provide(PostReactionRepo, provides=IPostReactionRepo)
    post_comment_repo = provide(PostCommentRepo, provides=IPostCommentRepo)
    post_comment_reaction_repo = provide(PostCommentReactionRepo, provides=IPostCommentReactionRepo)
    subscription_repo = provide(SubscriptionRepo, provides=ISubscriptionRepo)
