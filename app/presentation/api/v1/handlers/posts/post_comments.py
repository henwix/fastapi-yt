from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Request, status
from pydantic import HttpUrl

from app.application.common.pagination import CursorPagination
from app.application.posts.commands import CreatePostCommentCommand, DeletePostCommentCommand, UpdatePostCommentCommand
from app.application.posts.queries import GetPostCommentRepliesQuery, GetPostCommentsQuery, PostCommentsSorting
from app.application.posts.usecases import (
    CreatePostCommentUseCase,
    DeletePostCommentUseCase,
    GetPostCommentRepliesUseCase,
    GetPostCommentsUseCase,
    UpdatePostCommentUseCase,
)
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions.pagination import InvalidCursorError
from app.domain.posts.exceptions import PostCommentAccessForbiddenError, PostCommentNotFoundError, PostNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID
from app.presentation.api.v1.handlers.common.query_params import CursorPaginationParams
from app.presentation.api.v1.schemas.requests.posts import (
    CreatePostCommentInSchema,
    PostCommentsSortingParamsSchema,
    UpdatePostCommentInSchema,
)
from app.presentation.api.v1.schemas.responses.common import CursorPaginationResponse
from app.presentation.api.v1.schemas.responses.posts import DetailedPostCommentOutSchema, PostCommentOutSchema

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
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostNotFoundError,
            PostCommentNotFoundError,
        ),
    },
)
async def create_post_comment(
    current_channel_id: CurrentChannelID,
    post_id: UUID,
    schema: CreatePostCommentInSchema,
    use_case: FromDishka[CreatePostCommentUseCase],
) -> PostCommentOutSchema:
    command = CreatePostCommentCommand(
        current_channel_id=current_channel_id,
        post_id=post_id,
        **schema.model_dump(exclude_unset=True, exclude_none=True),
    )
    post_comment = await use_case.execute(command=command)
    return PostCommentOutSchema.from_entity(entity=post_comment)


@router.get(
    path='/posts/{post_id}/comments',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            InvalidCursorError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            PostNotFoundError,
        ),
    },
)
async def get_post_comments(
    post_id: UUID,
    sorting: Annotated[PostCommentsSortingParamsSchema, Depends()],
    pagination: CursorPaginationParams,
    use_case: FromDishka[GetPostCommentsUseCase],
    request: Request,
) -> CursorPaginationResponse[DetailedPostCommentOutSchema]:
    query = GetPostCommentsQuery(
        post_id=post_id,
        sorting=PostCommentsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    comments, cursor = await use_case.execute(query=query)
    return CursorPaginationResponse(
        next_page=HttpUrl(str(request.url.include_query_params(cursor=cursor))) if cursor else None,
        results=[DetailedPostCommentOutSchema.from_dto(dto=comment) for comment in comments],
    )


@router.get(
    path='/post_comments/{post_comment_id}/replies',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            InvalidCursorError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            PostCommentNotFoundError,
        ),
    },
)
async def get_post_comment_replies(
    post_comment_id: UUID,
    sorting: Annotated[PostCommentsSortingParamsSchema, Depends()],
    pagination: CursorPaginationParams,
    use_case: FromDishka[GetPostCommentRepliesUseCase],
    request: Request,
) -> CursorPaginationResponse[DetailedPostCommentOutSchema]:
    query = GetPostCommentRepliesQuery(
        post_comment_id=post_comment_id,
        sorting=PostCommentsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    replies, cursor = await use_case.execute(query=query)
    return CursorPaginationResponse(
        next_page=HttpUrl(str(request.url.include_query_params(cursor=cursor))) if cursor else None,
        results=[DetailedPostCommentOutSchema.from_dto(dto=reply) for reply in replies],
    )


@router.delete(
    path='/post_comments/{post_comment_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PostCommentAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundError,
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
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            PostCommentAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostCommentNotFoundError,
        ),
    },
)
async def update_post_comment(
    current_channel_id: CurrentChannelID,
    post_comment_id: UUID,
    schema: UpdatePostCommentInSchema,
    use_case: FromDishka[UpdatePostCommentUseCase],
) -> PostCommentOutSchema:
    command = UpdatePostCommentCommand(
        current_channel_id=current_channel_id,
        post_comment_id=post_comment_id,
        **schema.model_dump(exclude_unset=True),
    )
    post_comment = await use_case.execute(command=command)
    return PostCommentOutSchema.from_entity(entity=post_comment)
