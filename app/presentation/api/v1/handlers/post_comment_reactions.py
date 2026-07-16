from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status

from app.application.post_comment_reactions.commands import (
    CreatePostCommentReactionCommand,
    DeletePostCommentReactionCommand,
)
from app.application.post_comment_reactions.use_cases.create_post_comment_reaction import (
    CreatePostCommentReactionUseCase,
)
from app.application.post_comment_reactions.use_cases.delete_post_comment_reaction import (
    DeletePostCommentReactionUseCase,
)
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.post_comment_reactions.exceptions import (
    PostCommentReactionAlreadyExistsError,
    PostCommentReactionNotFoundError,
)
from app.domain.post_comments.exceptions import PostCommentNotFoundByIdError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.post_comment_reactions import (
    CreatePostCommentReactionInSchema,
    PostCommentReactionOutSchema,
)

router = APIRouter(
    prefix='/post_comments/{post_comment_id}/reactions',
    tags=['Post Comment Reactions'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    responses={
        status.HTTP_200_OK: {
            'model': PostCommentReactionOutSchema,
            'description': 'Returns an existing reaction, or updates it if *reaction_type* is different',
        },
        status.HTTP_201_CREATED: {
            'model': PostCommentReactionOutSchema,
            'description': 'Creates a new reaction',
        },
        status.HTTP_400_BAD_REQUEST: error_response(PostCommentReactionAlreadyExistsError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundByIdError,
            PostCommentReactionNotFoundError,
        ),
    },
)
async def create_post_comment_reaction(
    post_comment_id: UUID,
    current_channel_id: CurrentChannelID,
    schema: CreatePostCommentReactionInSchema,
    use_case: FromDishka[CreatePostCommentReactionUseCase],
    response: Response,
) -> PostCommentReactionOutSchema:
    command = CreatePostCommentReactionCommand(
        current_channel_id=current_channel_id,
        post_comment_id=post_comment_id,
        **schema.model_dump(),
    )
    reaction, is_created = await use_case.execute(command=command)
    if is_created:
        response.status_code = status.HTTP_201_CREATED
    return PostCommentReactionOutSchema.from_entity(entity=reaction)


@router.delete(
    path='',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundByIdError,
            PostCommentReactionNotFoundError,
        ),
    },
)
async def delete_post_comment_reaction(
    post_comment_id: UUID,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeletePostCommentReactionUseCase],
) -> None:
    command = DeletePostCommentReactionCommand(
        current_channel_id=current_channel_id,
        post_comment_id=post_comment_id,
    )
    await use_case.execute(command=command)
