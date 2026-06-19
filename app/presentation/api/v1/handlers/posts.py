from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.posts.commands import CreatePostCommand, DeletePostCommand, UpdatePostCommand
from app.application.posts.queries import GetPostQuery
from app.application.posts.use_cases.create_post import CreatePostUseCase
from app.application.posts.use_cases.delete_post import DeletePostUseCase
from app.application.posts.use_cases.get_post import GetPostUseCase
from app.application.posts.use_cases.update_post import UpdatePostUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.posts.exceptions import PostAccessForbiddenError, PostNotFoundByIdError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.posts import CreatePostSchema, GetPostSchema, UpdatePostSchema

router = APIRouter(
    prefix='/posts',
    tags=['Posts'],
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
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
    },
)
async def create_post(
    schema: CreatePostSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[CreatePostUseCase],
) -> GetPostSchema:
    command = CreatePostCommand(current_channel_id=current_channel_id, **schema.model_dump())
    post = await use_case.execute(command=command)
    return GetPostSchema.from_entity(entity=post)


@router.get(
    path='/{post_id}',
    responses={status.HTTP_404_NOT_FOUND: error_response(PostNotFoundByIdError)},
)
async def get_post(
    post_id: UUID,
    use_case: FromDishka[GetPostUseCase],
) -> GetPostSchema:
    query = GetPostQuery(post_id=post_id)
    post = await use_case.execute(query=query)
    return GetPostSchema.from_entity(entity=post)


@router.patch(
    path='/{post_id}',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError, PostAccessForbiddenError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError, PostNotFoundByIdError),
    },
)
async def update_post(
    post_id: UUID,
    schema: UpdatePostSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[UpdatePostUseCase],
) -> GetPostSchema:
    command = UpdatePostCommand(
        current_channel_id=current_channel_id,
        post_id=post_id,
        **schema.model_dump(exclude_unset=True),
    )
    post = await use_case.execute(command=command)
    return GetPostSchema.from_entity(entity=post)


@router.delete(
    path='/{post_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError, PostAccessForbiddenError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError, PostNotFoundByIdError),
    },
)
async def delete_post(
    post_id: UUID,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeletePostUseCase],
) -> None:
    command = DeletePostCommand(current_channel_id=current_channel_id, post_id=post_id)
    await use_case.execute(command=command)
