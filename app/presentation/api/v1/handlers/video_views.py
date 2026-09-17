from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.videos.commands.video_views import CreateVideoViewCommand
from app.application.videos.use_cases import CreateVideoViewUseCase
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_views.exceptions import VideoViewsLimitReachedError
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import AnonymousID, OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.path_params import PathVideoId

router = APIRouter(
    prefix='/videos/{video_id}/views',
    tags=['Video Views'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoViewsLimitReachedError,
        ),
    },
)
async def create_video_view(
    current_channel_id: OptionalCurrentChannelID,
    anonymous_id: AnonymousID,
    video_id: PathVideoId,
    use_case: FromDishka[CreateVideoViewUseCase],
) -> None:
    command = CreateVideoViewCommand(
        current_channel_id=current_channel_id,
        anonymous_id=anonymous_id,
        video_id=video_id,
    )
    await use_case.execute(command=command)
