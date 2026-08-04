from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.video_history.commands import (
    AddVideoToHistoryCommand,
    ClearVideoHistoryCommand,
    DeleteVideoFromHistoryCommand,
)
from app.application.video_history.use_cases.add_video_to_history import AddVideoToHistoryUseCase
from app.application.video_history.use_cases.clear_video_history import ClearVideoHistoryUseCase
from app.application.video_history.use_cases.delete_video_from_history import DeleteVideoFromHistoryUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_history.exceptions import VideoHistoryEmptyError, VideoNotFoundInHistoryError
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId

router = APIRouter(
    prefix='',
    tags=['Video History'],
    route_class=DishkaRoute,
)


@router.post(
    path='/videos/{video_id}/history',
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
        ),
    },
)
async def add_video_to_history(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[AddVideoToHistoryUseCase],
) -> None:
    command = AddVideoToHistoryCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
    )
    await use_case.execute(command=command)


@router.delete(
    path='/videos/{video_id}/history',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundInHistoryError,
        ),
    },
)
async def delete_video_from_history(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[DeleteVideoFromHistoryUseCase],
) -> None:
    command = DeleteVideoFromHistoryCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
    )
    await use_case.execute(command=command)


@router.delete(
    path='/history',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoHistoryEmptyError,
        ),
    },
)
async def clear_video_history(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[ClearVideoHistoryUseCase],
) -> None:
    command = ClearVideoHistoryCommand(current_channel_id=current_channel_id)
    await use_case.execute(command=command)
