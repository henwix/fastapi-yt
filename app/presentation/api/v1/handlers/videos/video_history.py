from typing import Annotated

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Request, status
from pydantic import HttpUrl

from app.application.common.pagination import CursorPagination
from app.application.videos.commands import (
    AddVideoToHistoryCommand,
    ClearVideoHistoryCommand,
    DeleteVideoFromHistoryCommand,
)
from app.application.videos.queries import GetVideoHistoryQuery, VideoHistorySorting
from app.application.videos.usecases import (
    AddVideoToHistoryUseCase,
    ClearVideoHistoryUseCase,
    DeleteVideoFromHistoryUseCase,
    GetVideoHistoryUseCase,
)
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions.pagination import InvalidCursorError
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoHistoryEmptyError,
    VideoNotFoundError,
    VideoNotFoundInHistoryError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID
from app.presentation.api.v1.handlers.common.path_params import PathVideoId
from app.presentation.api.v1.handlers.common.query_params import CursorPaginationParams
from app.presentation.api.v1.schemas.requests.videos import VideoHistorySortingParamsSchema
from app.presentation.api.v1.schemas.responses.common import CursorPaginationResponse
from app.presentation.api.v1.schemas.responses.videos import PreviewVideoHistoryOutSchema

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
            JWTTokenExpiredError,
            JWTTokenInvalidError,
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
            JWTTokenExpiredError,
            JWTTokenInvalidError,
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


@router.get(
    '/history',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            InvalidCursorError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def get_video_history(
    current_channel_id: CurrentChannelID,
    sorting: Annotated[VideoHistorySortingParamsSchema, Depends()],
    pagination: CursorPaginationParams,
    use_case: FromDishka[GetVideoHistoryUseCase],
    request: Request,
) -> CursorPaginationResponse[PreviewVideoHistoryOutSchema]:
    query = GetVideoHistoryQuery(
        current_channel_id=current_channel_id,
        sorting=VideoHistorySorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    videos, cursor = await use_case.execute(query=query)
    return CursorPaginationResponse(
        next_page=HttpUrl(str(request.url.include_query_params(cursor=cursor))) if cursor else None,
        results=[PreviewVideoHistoryOutSchema.from_dto(dto=video) for video in videos],
    )
