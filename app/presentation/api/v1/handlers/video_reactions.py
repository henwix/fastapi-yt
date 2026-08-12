from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.video_reactions.commands import CreateVideoReactionCommand, DeleteVideoReactionCommand
from app.application.video_reactions.use_cases.create_video_reaction import CreateVideoReactionUseCase
from app.application.video_reactions.use_cases.delete_video_reaction import DeleteVideoReactionUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_reactions.exceptions import VideoReactionNotFoundError
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.requests.video_reactions import CreateVideoReactionInSchema
from app.presentation.api.v1.schemas.responses.video_reactions import VideoReactionOutSchema

router = APIRouter(
    prefix='/videos/{video_id}/reactions',
    tags=['Video Reactions'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'model': VideoReactionOutSchema,
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
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
    },
)
async def create_video_reaction(
    current_channel_id: CurrentChannelID,
    schema: CreateVideoReactionInSchema,
    video_id: PathVideoId,
    response: Response,
    use_case: FromDishka[CreateVideoReactionUseCase],
) -> VideoReactionOutSchema | None:
    command = CreateVideoReactionCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(),
    )
    video_reaction = await use_case.execute(command=command)
    if video_reaction is None:
        response.status_code = status.HTTP_204_NO_CONTENT
        return
    return VideoReactionOutSchema.from_entity(entity=video_reaction)


@router.delete(
    path='',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
            VideoReactionNotFoundError,
        ),
    },
)
async def delete_video_reaction(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[DeleteVideoReactionUseCase],
) -> None:
    command = DeleteVideoReactionCommand(current_channel_id=current_channel_id, video_id=video_id)
    await use_case.execute(command=command)
