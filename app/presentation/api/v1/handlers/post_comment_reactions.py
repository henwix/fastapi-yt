from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.post_comment_reactions import (
    CreatePostCommentReactionSchema,
    PostCommentReactionSchema,
)

router = APIRouter(
    prefix='/post_comments/{post_comment_id}/reactions',
    tags=['Post Comment Reactions'],
    route_class=DishkaRoute,
)


@router.post(path='')
async def create_post_comment_reaction(
    post_comment_id: UUID,
    current_channel_id: CurrentChannelID,
    schema: CreatePostCommentReactionSchema,
) -> PostCommentReactionSchema: ...
