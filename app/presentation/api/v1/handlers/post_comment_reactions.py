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
    PostCommentReactionNotFoundError,
)
from app.domain.post_comments.exceptions import PostCommentNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.requests.post_comment_reactions import CreatePostCommentReactionInSchema
from app.presentation.api.v1.schemas.responses.post_comment_reactions import PostCommentReactionOutSchema

router = APIRouter(
    prefix='/post_comments/{post_comment_id}/reactions',
    tags=['Post Comment Reactions'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'model': PostCommentReactionOutSchema,
            'description': 'Returns a new reaction or updates an existing one if *reaction_type* is different',
        },
        status.HTTP_204_NO_CONTENT: {
            'description': 'Returns nothing if a reaction with the same *reaction_type* already exists',
        },
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundError,
        ),
    },
)
async def create_post_comment_reaction(
    post_comment_id: UUID,
    current_channel_id: CurrentChannelID,
    schema: CreatePostCommentReactionInSchema,
    use_case: FromDishka[CreatePostCommentReactionUseCase],
    response: Response,
) -> PostCommentReactionOutSchema | None:
    command = CreatePostCommentReactionCommand(
        current_channel_id=current_channel_id,
        post_comment_id=post_comment_id,
        **schema.model_dump(),
    )
    reaction = await use_case.execute(command=command)
    if reaction is None:
        response.status_code = status.HTTP_204_NO_CONTENT
        return
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
            PostCommentNotFoundError,
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
