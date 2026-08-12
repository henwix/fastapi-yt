from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.video_comment_reactions.commands import (
    CreateVideoCommentReactionCommand,
    DeleteVideoCommentReactionCommand,
)
from app.application.video_comment_reactions.use_cases.create_video_comment_reaction import (
    CreateVideoCommentReactionUseCase,
)
from app.application.video_comment_reactions.use_cases.delete_video_comment_reaction import (
    DeleteVideoCommentReactionUseCase,
)
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_comment_reactions.exceptions import VideoCommentReactionNotFoundError
from app.domain.video_comments.exceptions import VideoCommentNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.requests.video_comment_reactions import CreateVideoCommentReactionInSchema
from app.presentation.api.v1.schemas.responses.video_comment_reactions import VideoCommentReactionOutSchema

router = APIRouter(
    prefix='/video_comments/{video_comment_id}/reactions',
    tags=['Video Comment Reactions'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'model': VideoCommentReactionOutSchema,
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
            VideoCommentNotFoundError,
        ),
    },
)
async def create_video_comment_reaction(
    video_comment_id: UUID,
    current_channel_id: CurrentChannelID,
    schema: CreateVideoCommentReactionInSchema,
    use_case: FromDishka[CreateVideoCommentReactionUseCase],
    response: Response,
) -> VideoCommentReactionOutSchema | None:
    command = CreateVideoCommentReactionCommand(
        current_channel_id=current_channel_id,
        video_comment_id=video_comment_id,
        **schema.model_dump(),
    )
    reaction = await use_case.execute(command=command)
    if reaction is None:
        response.status_code = status.HTTP_204_NO_CONTENT
        return
    return VideoCommentReactionOutSchema.from_entity(entity=reaction)


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
            VideoCommentNotFoundError,
            VideoCommentReactionNotFoundError,
        ),
    },
)
async def delete_video_comment_reaction(
    video_comment_id: UUID,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeleteVideoCommentReactionUseCase],
) -> None:
    command = DeleteVideoCommentReactionCommand(
        current_channel_id=current_channel_id,
        video_comment_id=video_comment_id,
    )
    await use_case.execute(command=command)
