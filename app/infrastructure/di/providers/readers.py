from dishka import Provider, Scope, provide

from app.application.channels.interfaces import IChannelReader
from app.application.oauth.interfaces import IOAuthAccountReader
from app.application.playlists.interfaces import IPlaylistReader
from app.application.posts.interfaces import IPostCommentReader, IPostReader
from app.application.subscriptions.interfaces import ISubscriptionReader
from app.application.videos.interfaces import IVideoCommentReader, IVideoHistoryReader, IVideoReader
from app.infrastructure.sqlalchemy.readers import (
    ChannelReader,
    OAuthAccountReader,
    PlaylistReader,
    PostCommentReader,
    PostReader,
    SubscriptionReader,
    VideoCommentReader,
    VideoHistoryReader,
    VideoReader,
)


class ReadersProvider(Provider):
    scope = Scope.REQUEST

    channel_reader = provide(ChannelReader, provides=IChannelReader)
    oauth_account_reader = provide(OAuthAccountReader, provides=IOAuthAccountReader)
    post_reader = provide(PostReader, provides=IPostReader)
    post_comment_reader = provide(PostCommentReader, provides=IPostCommentReader)
    subscription_reader = provide(SubscriptionReader, provides=ISubscriptionReader)
    video_reader = provide(VideoReader, provides=IVideoReader)
    video_comment_reader = provide(VideoCommentReader, provides=IVideoCommentReader)
    video_history_reader = provide(VideoHistoryReader, provides=IVideoHistoryReader)
    playlist_reader = provide(PlaylistReader, provides=IPlaylistReader)
