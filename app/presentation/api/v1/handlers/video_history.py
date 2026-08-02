from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.video_history.commands import AddVideoToHistoryCommand
from app.application.video_history.use_cases.add_video_to_history import AddVideoToHistoryUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
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
