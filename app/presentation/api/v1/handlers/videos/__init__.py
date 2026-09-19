from .video_comment_reactions import router as video_comment_reactions_router
from .video_comments import router as video_comments_router
from .video_history import router as video_history_router
from .video_reactions import router as video_reactions_router
from .video_uploads import router as video_uploads_router
from .video_views import router as video_views_router
from .videos import router as videos_router

__all__ = (
    'video_comment_reactions_router',
    'video_comments_router',
    'video_history_router',
    'video_reactions_router',
    'video_uploads_router',
    'video_views_router',
    'videos_router',
)
