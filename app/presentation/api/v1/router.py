from fastapi import APIRouter

from app.presentation.api.v1.handlers.auth import router as auth_router
from app.presentation.api.v1.handlers.channels import router as channels_router
from app.presentation.api.v1.handlers.playlists import router as playlists_router
from app.presentation.api.v1.handlers.post_comment_reactions import router as post_comment_reactions_router
from app.presentation.api.v1.handlers.post_comments import router as post_comments_router
from app.presentation.api.v1.handlers.post_reactions import router as post_reactions_router
from app.presentation.api.v1.handlers.posts import router as posts_router
from app.presentation.api.v1.handlers.subscriptions import router as subscriptions_router
from app.presentation.api.v1.handlers.video_reactions import router as video_reactions_router
from app.presentation.api.v1.handlers.video_uploads import router as video_uploads_router
from app.presentation.api.v1.handlers.videos import router as videos_router

v1_router = APIRouter()
v1_router.include_router(router=auth_router)
v1_router.include_router(router=channels_router)
v1_router.include_router(router=subscriptions_router)
v1_router.include_router(router=video_uploads_router)
v1_router.include_router(router=videos_router)
v1_router.include_router(router=video_reactions_router)
v1_router.include_router(router=playlists_router)
v1_router.include_router(router=posts_router)
v1_router.include_router(router=post_reactions_router)
v1_router.include_router(router=post_comments_router)
v1_router.include_router(router=post_comment_reactions_router)
