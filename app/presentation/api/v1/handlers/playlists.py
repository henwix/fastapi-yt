from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Path, Request, status

from app.application.common.pagination import CursorPagination
from app.application.playlists.commands import (
    AddVideoToPlaylistCommand,
    CreatePlaylistCommand,
    DeletePlaylistCommand,
    DeleteVideoFromPlaylistCommand,
    UpdatePlaylistCommand,
)
from app.application.playlists.queries import (
    GetChannelPlaylistsQuery,
    GetPersonalPlaylistsQuery,
    GetPlaylistQuery,
    PlaylistsPreviewSorting,
)
from app.application.playlists.use_cases.add_video_to_playlist import AddVideoToPlaylistUseCase
from app.application.playlists.use_cases.create_playlist import CreatePlaylistUseCase
from app.application.playlists.use_cases.delete_playlist import DeletePlaylistUseCase
from app.application.playlists.use_cases.delete_video_from_playlist import DeleteVideoFromPlaylistUseCase
from app.application.playlists.use_cases.get_channel_playlists import GetChannelPlaylistsUseCase
from app.application.playlists.use_cases.get_personal_playlists import GetPersonalPlaylistsUseCase
from app.application.playlists.use_cases.get_playlist import GetPlaylistUseCase
from app.application.playlists.use_cases.update_playlist import UpdatePlaylistUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError, ChannelNotFoundBySlugError
from app.domain.common.constants import SLUG_PATTERN
from app.domain.common.exceptions import InvalidCursorError
from app.domain.playlists.exceptions import (
    PlaylistAccessForbiddenError,
    PlaylistNotFoundError,
    VideoAlreadyAddedToPlaylistError,
    VideoNotFoundInPlaylistError,
)
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.common import CursorPaginationParams
from app.presentation.api.v1.schemas.playlists import (
    CreatePlaylistInSchema,
    DetailedPlaylistOutSchema,
    GetPlaylistsPreviewSortingParams,
    PlaylistOutSchema,
    PreviewPlaylistOutSchema,
    PreviewPlaylistsCursorResponse,
    UpdatePlaylistInSchema,
)

router = APIRouter(
    prefix='',
    tags=['Playlists'],
    route_class=DishkaRoute,
)


@router.post(
    path='/playlists',
    status_code=status.HTTP_201_CREATED,
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
        ),
    },
)
async def create_playlist(
    current_channel_id: CurrentChannelID,
    schema: CreatePlaylistInSchema,
    use_case: FromDishka[CreatePlaylistUseCase],
) -> PlaylistOutSchema:
    command = CreatePlaylistCommand(current_channel_id=current_channel_id, **schema.model_dump())
    playlist = await use_case.execute(command=command)
    return PlaylistOutSchema.from_entity(entity=playlist)


@router.get(
    '/playlists/personal',
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
async def get_personal_playlists(
    current_channel_id: CurrentChannelID,
    sorting: Annotated[GetPlaylistsPreviewSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetPersonalPlaylistsUseCase],
    request: Request,
) -> PreviewPlaylistsCursorResponse:
    query = GetPersonalPlaylistsQuery(
        current_channel_id=current_channel_id,
        sorting=PlaylistsPreviewSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    playlists, next_cursor = await use_case.execute(query=query)
    return PreviewPlaylistsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=next_cursor)) if next_cursor is not None else None,
        results=[PreviewPlaylistOutSchema.from_dto(dto=playlist) for playlist in playlists],
    )


@router.get(
    path='/channels/{channel_slug}/playlists',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(InvalidCursorError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundBySlugError,
        ),
    },
)
async def get_channel_playlists(
    channel_slug: Annotated[str, Path(min_length=1, max_length=40, pattern=SLUG_PATTERN)],
    sorting: Annotated[GetPlaylistsPreviewSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetChannelPlaylistsUseCase],
    request: Request,
) -> PreviewPlaylistsCursorResponse:
    query = GetChannelPlaylistsQuery(
        channel_slug=channel_slug,
        sorting=PlaylistsPreviewSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    playlists, next_cursor = await use_case.execute(query=query)
    return PreviewPlaylistsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=next_cursor)) if next_cursor is not None else None,
        results=[PreviewPlaylistOutSchema.from_dto(dto=playlist) for playlist in playlists],
    )


@router.get(
    path='/playlists/{playlist_id}',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PlaylistAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PlaylistNotFoundError,
        ),
    },
)
async def get_playlist(
    current_channel_id: OptionalCurrentChannelID,
    playlist_id: UUID,
    use_case: FromDishka[GetPlaylistUseCase],
) -> DetailedPlaylistOutSchema:
    query = GetPlaylistQuery(
        current_channel_id=current_channel_id,
        playlist_id=playlist_id,
    )
    playlist = await use_case.execute(query=query)
    return DetailedPlaylistOutSchema.from_dto(dto=playlist)


@router.delete(
    path='/playlists/{playlist_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PlaylistAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PlaylistNotFoundError,
        ),
    },
)
async def delete_playlist(
    current_channel_id: CurrentChannelID,
    playlist_id: UUID,
    use_case: FromDishka[DeletePlaylistUseCase],
) -> None:
    command = DeletePlaylistCommand(
        current_channel_id=current_channel_id,
        playlist_id=playlist_id,
    )
    await use_case.execute(command=command)


@router.patch(
    '/playlists/{playlist_id}',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PlaylistAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PlaylistNotFoundError,
        ),
    },
)
async def update_playlist(
    current_channel_id: CurrentChannelID,
    playlist_id: UUID,
    schema: UpdatePlaylistInSchema,
    use_case: FromDishka[UpdatePlaylistUseCase],
) -> PlaylistOutSchema:
    command = UpdatePlaylistCommand(
        current_channel_id=current_channel_id,
        playlist_id=playlist_id,
        **schema.model_dump(exclude_unset=True),
    )
    playlist = await use_case.execute(command=command)
    return PlaylistOutSchema.from_entity(entity=playlist)


@router.post(
    path='/playlists/{playlist_id}/videos/{video_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(VideoAlreadyAddedToPlaylistError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PlaylistAccessForbiddenError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PlaylistNotFoundError,
            VideoNotFoundError,
        ),
    },
)
async def add_video_to_playlist(
    current_channel_id: CurrentChannelID,
    playlist_id: UUID,
    video_id: PathVideoId,
    use_case: FromDishka[AddVideoToPlaylistUseCase],
) -> None:
    command = AddVideoToPlaylistCommand(
        current_channel_id=current_channel_id,
        playlist_id=playlist_id,
        video_id=video_id,
    )
    await use_case.execute(command=command)


@router.delete(
    path='/playlists/{playlist_id}/videos/{video_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PlaylistAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PlaylistNotFoundError,
            VideoNotFoundError,
            VideoNotFoundInPlaylistError,
        ),
    },
)
async def delete_video_from_playlist(
    current_channel_id: CurrentChannelID,
    playlist_id: UUID,
    video_id: PathVideoId,
    use_case: FromDishka[DeleteVideoFromPlaylistUseCase],
) -> None:
    command = DeleteVideoFromPlaylistCommand(
        current_channel_id=current_channel_id,
        playlist_id=playlist_id,
        video_id=video_id,
    )
    await use_case.execute(command=command)
