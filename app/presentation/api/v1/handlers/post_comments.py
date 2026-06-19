from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.post_comments.commands import CreatePostCommentCommand
from app.application.post_comments.use_cases.create_post_comment import CreatePostCommentUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.post_comments.exceptions import PostCommentNotFoundByIdError
from app.domain.posts.exceptions import PostNotFoundByIdError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.post_comments import CreatePostCommentSchema, PostCommentSchema

router = APIRouter(
    prefix='',
    tags=['Post Comments'],
    route_class=DishkaRoute,
)


@router.post(
    '/posts/{post_id}/comments',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostNotFoundByIdError,
            PostCommentNotFoundByIdError,
        ),
    },
)
async def create_post_comment(
    current_channel_id: CurrentChannelID,
    post_id: UUID,
    schema: CreatePostCommentSchema,
    use_case: FromDishka[CreatePostCommentUseCase],
) -> PostCommentSchema:
    command = CreatePostCommentCommand(
        current_channel_id=current_channel_id,
        post_id=post_id,
        **schema.model_dump(exclude_unset=True, exclude_none=True),
    )
    post_comment = await use_case.execute(command=command)
    return PostCommentSchema.from_entity(entity=post_comment)
