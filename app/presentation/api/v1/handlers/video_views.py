from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.video_views.commands import CreateVideoViewCommand
from app.application.video_views.use_cases.create_video_view import CreateVideoViewUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.video_views.exceptions import VideoViewsLimitReached
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.anonymous_id import AnonymousID
from app.presentation.api.v1.di.current_channel_id import OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId

router = APIRouter(
    prefix='/videos/{video_id}/views',
    tags=['Video Views'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(VideoViewsLimitReached),
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
