from fastapi import APIRouter

from .auth import router as auth_router
from .channels import router as channels_router
from .oauth import router as oauth_router
from .playlists import router as playlists_router
from .posts import post_comment_reactions_router, post_comments_router, post_reactions_router, posts_router
from .subscriptions import router as subscriptions_router
from .videos import (
    video_comment_reactions_router,
    video_comments_router,
    video_history_router,
    video_reactions_router,
    video_uploads_router,
    video_views_router,
    videos_router,
)

v1_router = APIRouter()
v1_router.include_router(router=auth_router)
v1_router.include_router(router=oauth_router)
v1_router.include_router(router=channels_router)
v1_router.include_router(router=subscriptions_router)
v1_router.include_router(router=video_uploads_router)
v1_router.include_router(router=videos_router)
v1_router.include_router(router=video_views_router)
v1_router.include_router(router=video_reactions_router)
v1_router.include_router(router=video_comments_router)
v1_router.include_router(router=video_comment_reactions_router)
v1_router.include_router(router=video_history_router)
v1_router.include_router(router=playlists_router)
v1_router.include_router(router=posts_router)
v1_router.include_router(router=post_reactions_router)
v1_router.include_router(router=post_comments_router)
v1_router.include_router(router=post_comment_reactions_router)


__all__ = ('v1_router',)
