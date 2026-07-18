from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.video_reactions.commands import CreateVideoReactionCommand, DeleteVideoReactionCommand
from app.application.video_reactions.use_cases.create_video_reaction import CreateVideoReactionUseCase
from app.application.video_reactions.use_cases.delete_video_reaction import DeleteVideoReactionUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_reactions.exceptions import VideoReactionAlreadyExistsError, VideoReactionNotFoundError
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundByIdError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.video_reactions import CreateVideoReactionInSchema, VideoReactionOutSchema

router = APIRouter(
    prefix='/videos/{video_id}/reactions',
    tags=['Video Reactions'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    responses={
        status.HTTP_200_OK: {
            'model': VideoReactionOutSchema,
            'description': 'Returns an existing reaction, or updates it if *reaction_type* is different',
        },
        status.HTTP_201_CREATED: {
            'model': VideoReactionOutSchema,
            'description': 'Creates a new reaction',
        },
        status.HTTP_400_BAD_REQUEST: error_response(VideoReactionAlreadyExistsError),
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
            VideoNotFoundByIdError,
            VideoReactionNotFoundError,
        ),
    },
)
async def create_video_reaction(
    current_channel_id: CurrentChannelID,
    schema: CreateVideoReactionInSchema,
    video_id: PathVideoId,
    response: Response,
    use_case: FromDishka[CreateVideoReactionUseCase],
) -> VideoReactionOutSchema:
    command = CreateVideoReactionCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(),
    )
    video_reaction, is_created = await use_case.execute(command=command)
    if is_created:
        response.status_code = status.HTTP_201_CREATED
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
            VideoNotFoundByIdError,
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
