from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.playlists.commands import (
    AddVideoToPlaylistCommand,
    CreatePlaylistCommand,
    DeletePlaylistCommand,
    DeleteVideoFromPlaylistCommand,
    UpdatePlaylistCommand,
)
from app.application.playlists.queries import GetPlaylistQuery
from app.application.playlists.use_cases.add_video_to_playlist import AddVideoToPlaylistUseCase
from app.application.playlists.use_cases.create_playlist import CreatePlaylistUseCase
from app.application.playlists.use_cases.delete_playlist import DeletePlaylistUseCase
from app.application.playlists.use_cases.delete_video_from_playlist import DeleteVideoFromPlaylistUseCase
from app.application.playlists.use_cases.get_playlist import GetPlaylistUseCase
from app.application.playlists.use_cases.update_playlist import UpdatePlaylistUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
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
from app.presentation.api.v1.schemas.playlists import (
    CreatePlaylistInSchema,
    DetailedPlaylistOutSchema,
    PlaylistOutSchema,
    UpdatePlaylistInSchema,
)

router = APIRouter(
    prefix='/playlists',
    tags=['Playlists'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
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
    path='/{playlist_id}',
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
    path='/{playlist_id}',
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
    '/{playlist_id}',
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
    path='/{playlist_id}/videos/{video_id}',
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
    path='/{playlist_id}/videos/{video_id}',
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
