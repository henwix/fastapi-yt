from typing import Annotated
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Request, status

from app.application.common.pagination import CursorPagination
from app.application.video_comments.commands import (
    CreateVideoCommentCommand,
    DeleteVideoCommentCommand,
    UpdateVideoCommentCommand,
)
from app.application.video_comments.queries import (
    GetVideoCommentRepliesQuery,
    GetVideoCommentsQuery,
    VideoCommentsSorting,
)
from app.application.video_comments.use_cases.create_video_comment import CreateVideoCommentUseCase
from app.application.video_comments.use_cases.delete_video_comment import DeleteVideoCommentUseCase
from app.application.video_comments.use_cases.get_video_comment_replies import GetVideoCommentRepliesUseCase
from app.application.video_comments.use_cases.get_video_comments import GetVideoCommentsUseCase
from app.application.video_comments.use_cases.update_video_comment import UpdateVideoCommentUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions import InvalidCursorError
from app.domain.video_comments.exceptions import VideoCommentAccessForbiddenError, VideoCommentNotFoundError
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.common import CursorPaginationParams
from app.presentation.api.v1.schemas.requests.video_comments import (
    CreateVideoCommentInSchema,
    UpdateVideoCommentInSchema,
    VideoCommentsSortingParams,
)
from app.presentation.api.v1.schemas.responses.video_comments import (
    DetailedVideoCommentOutSchema,
    VideoCommentOutSchema,
    VideoCommentsCursorResponse,
)

router = APIRouter(
    prefix='',
    tags=['Video Comments'],
    route_class=DishkaRoute,
)


@router.post(
    path='/videos/{video_id}/comments',
    status_code=status.HTTP_201_CREATED,
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
            VideoCommentNotFoundError,
        ),
    },
)
async def create_video_comment(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: CreateVideoCommentInSchema,
    use_case: FromDishka[CreateVideoCommentUseCase],
) -> VideoCommentOutSchema:
    command = CreateVideoCommentCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(exclude_unset=True, exclude_none=True),
    )
    video_comment = await use_case.execute(command=command)
    return VideoCommentOutSchema.from_entity(entity=video_comment)


@router.get(
    path='/videos/{video_id}/comments',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(InvalidCursorError),
        status.HTTP_404_NOT_FOUND: error_response(VideoNotFoundError),
    },
)
async def get_video_comments(
    video_id: PathVideoId,
    sorting: Annotated[VideoCommentsSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetVideoCommentsUseCase],
    request: Request,
) -> VideoCommentsCursorResponse:
    query = GetVideoCommentsQuery(
        video_id=video_id,
        sorting=VideoCommentsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    comments, cursor = await use_case.execute(query=query)
    return VideoCommentsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[DetailedVideoCommentOutSchema.from_dto(dto=comment) for comment in comments],
    )


@router.get(
    path='/video_comments/{video_comment_id}/replies',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(InvalidCursorError),
        status.HTTP_404_NOT_FOUND: error_response(VideoCommentNotFoundError),
    },
)
async def get_video_comment_replies(
    video_comment_id: UUID,
    sorting: Annotated[VideoCommentsSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetVideoCommentRepliesUseCase],
    request: Request,
) -> VideoCommentsCursorResponse:
    query = GetVideoCommentRepliesQuery(
        video_comment_id=video_comment_id,
        sorting=VideoCommentsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    replies, cursor = await use_case.execute(query=query)
    return VideoCommentsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[DetailedVideoCommentOutSchema.from_dto(dto=reply) for reply in replies],
    )


@router.delete(
    path='/video_comments/{video_comment_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoCommentAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoCommentNotFoundError,
        ),
    },
)
async def delete_video_comment(
    current_channel_id: CurrentChannelID,
    video_comment_id: UUID,
    use_case: FromDishka[DeleteVideoCommentUseCase],
) -> None:
    command = DeleteVideoCommentCommand(
        current_channel_id=current_channel_id,
        video_comment_id=video_comment_id,
    )
    await use_case.execute(command=command)


@router.patch(
    path='/video_comments/{video_comment_id}',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoCommentAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoCommentNotFoundError,
        ),
    },
)
async def update_video_comment(
    current_channel_id: CurrentChannelID,
    video_comment_id: UUID,
    schema: UpdateVideoCommentInSchema,
    use_case: FromDishka[UpdateVideoCommentUseCase],
) -> VideoCommentOutSchema:
    command = UpdateVideoCommentCommand(
        current_channel_id=current_channel_id,
        video_comment_id=video_comment_id,
        **schema.model_dump(exclude_unset=True),
    )
    video_comment = await use_case.execute(command=command)
    return VideoCommentOutSchema.from_entity(entity=video_comment)
