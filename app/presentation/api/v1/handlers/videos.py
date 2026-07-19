from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Request, status

from app.application.common.pagination import CursorPagination
from app.application.videos.commands import (
    DeleteVideoCommand,
    UpdateVideoCommand,
)
from app.application.videos.queries import (
    GetPersonalVideosFilters,
    GetPersonalVideosQuery,
    GetPersonalVideosSorting,
    GetVideoQuery,
)
from app.application.videos.use_cases.delete_video import DeleteVideoUseCase
from app.application.videos.use_cases.get_personal_videos import GetPersonalVideosUseCase
from app.application.videos.use_cases.get_video import GetVideoUseCase
from app.application.videos.use_cases.update_video import UpdateVideoUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions import InvalidCursorError
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoNotFoundError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.common import CursorPaginationParams
from app.presentation.api.v1.schemas.videos import (
    DetailedVideoOutSchema,
    PersonalVideoPreviewOutSchema,
    PersonalVideosCursorResponse,
    PersonalVideosFiltersParams,
    PersonalVideosSortingParams,
    UpdateVideoInSchema,
    VideoOutSchema,
)

router = APIRouter(
    prefix='/videos',
    tags=['Videos'],
    route_class=DishkaRoute,
)


@router.get(
    path='/personal',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(InvalidCursorError),
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
        ),
    },
)
async def get_personal_videos(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[GetPersonalVideosUseCase],
    filters: Annotated[PersonalVideosFiltersParams, Depends()],
    sorting: Annotated[PersonalVideosSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    request: Request,
) -> PersonalVideosCursorResponse:
    query = GetPersonalVideosQuery(
        current_channel_id=current_channel_id,
        filters=GetPersonalVideosFilters(**filters.model_dump(exclude_none=True)),
        sorting=GetPersonalVideosSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    videos, cursor = await use_case.execute(query=query)
    return PersonalVideosCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[PersonalVideoPreviewOutSchema.from_dto(dto=video) for video in videos],
    )


@router.delete(
    path='/{video_id}',
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
async def delete_video(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[DeleteVideoUseCase],
) -> None:
    command = DeleteVideoCommand(current_channel_id=current_channel_id, video_id=video_id)
    await use_case.execute(command=command)


@router.get(
    path='/{video_id}',
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
async def get_video(
    current_channel_id: OptionalCurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[GetVideoUseCase],
) -> DetailedVideoOutSchema:
    query = GetVideoQuery(current_channel_id=current_channel_id, video_id=video_id)
    video = await use_case.execute(query=query)
    return DetailedVideoOutSchema.from_dto(dto=video)


@router.patch(
    path='/{video_id}',
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
async def update_video(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: UpdateVideoInSchema,
    use_case: FromDishka[UpdateVideoUseCase],
) -> VideoOutSchema:
    command = UpdateVideoCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(exclude_unset=True),
    )
    video = await use_case.execute(command=command)
    return VideoOutSchema.from_entity(entity=video)
