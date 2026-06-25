from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Request, status

from app.application.common.pagination import CursorPagination
from app.application.post_comments.commands import (
    CreatePostCommentCommand,
    DeletePostCommentCommand,
    UpdatePostCommentCommand,
)
from app.application.post_comments.queries import GetPostCommentRepliesQuery, GetPostCommentsQuery, PostCommentsSorting
from app.application.post_comments.use_cases.create_post_comment import CreatePostCommentUseCase
from app.application.post_comments.use_cases.delete_post_comment import DeletePostCommentUseCase
from app.application.post_comments.use_cases.get_post_comment_replies import GetPostCommentRepliesUseCase
from app.application.post_comments.use_cases.get_post_comments import GetPostCommentsUseCase
from app.application.post_comments.use_cases.update_post_comment import UpdatePostCommentUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.post_comments.exceptions import PostCommentAccessForbiddenError, PostCommentNotFoundByIdError
from app.domain.posts.exceptions import PostNotFoundByIdError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.base import CursorPaginationParams
from app.presentation.api.v1.schemas.post_comments import (
    CreatePostCommentSchema,
    DetailedPostCommentSchema,
    PostCommentSchema,
    PostCommentsCursorResponse,
    PostCommentsSortingParams,
    UpdatePostCommentSchema,
)

router = APIRouter(
    prefix='',
    tags=['Post Comments'],
    route_class=DishkaRoute,
)


@router.post(
    path='/posts/{post_id}/comments',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostNotFoundByIdError,
            PostCommentNotFoundByIdError,
        ),
    },
)
async def create_post_comment(
    current_channel_id: CurrentChannelID,
    post_id: UUID,
    schema: CreatePostCommentSchema,
    use_case: FromDishka[CreatePostCommentUseCase],
) -> PostCommentSchema:
    command = CreatePostCommentCommand(
        current_channel_id=current_channel_id,
        post_id=post_id,
        **schema.model_dump(exclude_unset=True, exclude_none=True),
    )
    post_comment = await use_case.execute(command=command)
    return PostCommentSchema.from_entity(entity=post_comment)


@router.get(
    path='/posts/{post_id}/comments',
    responses={
        status.HTTP_404_NOT_FOUND: error_response(PostNotFoundByIdError),
    },
)
async def get_post_comments(
    post_id: UUID,
    sorting: Annotated[PostCommentsSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetPostCommentsUseCase],
    request: Request,
) -> PostCommentsCursorResponse:
    query = GetPostCommentsQuery(
        post_id=post_id,
        sorting=PostCommentsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    comments, cursor = await use_case.execute(query=query)
    return PostCommentsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[DetailedPostCommentSchema.from_dto(dto=comment) for comment in comments],
    )


@router.get(
    path='/post_comments/{post_comment_id}/replies',
    responses={
        status.HTTP_404_NOT_FOUND: error_response(PostCommentNotFoundByIdError),
    },
)
async def get_post_comment_replies(
    post_comment_id: UUID,
    sorting: Annotated[PostCommentsSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetPostCommentRepliesUseCase],
    request: Request,
) -> PostCommentsCursorResponse:
    query = GetPostCommentRepliesQuery(
        post_comment_id=post_comment_id,
        sorting=PostCommentsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    replies, cursor = await use_case.execute(query=query)
    return PostCommentsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[DetailedPostCommentSchema.from_dto(dto=reply) for reply in replies],
    )


@router.delete(
    path='/post_comments/{post_comment_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PostCommentAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundByIdError,
        ),
    },
)
async def delete_post_comment(
    current_channel_id: CurrentChannelID,
    post_comment_id: UUID,
    use_case: FromDishka[DeletePostCommentUseCase],
) -> None:
    command = DeletePostCommentCommand(
        current_channel_id=current_channel_id,
        post_comment_id=post_comment_id,
    )
    await use_case.execute(command=command)


@router.patch(
    path='/post_comments/{post_comment_id}',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PostCommentAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundByIdError,
        ),
    },
)
async def update_post_comment(
    current_channel_id: CurrentChannelID,
    post_comment_id: UUID,
    schema: UpdatePostCommentSchema,
    use_case: FromDishka[UpdatePostCommentUseCase],
) -> PostCommentSchema:
    command = UpdatePostCommentCommand(
        current_channel_id=current_channel_id,
        post_comment_id=post_comment_id,
        **schema.model_dump(exclude_unset=True),
    )
    post_comment = await use_case.execute(command=command)
    return PostCommentSchema.from_entity(entity=post_comment)
