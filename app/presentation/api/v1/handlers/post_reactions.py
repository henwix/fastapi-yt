from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Response, status

from app.application.post_reactions.commands import CreatePostReactionCommand, DeletePostReactionCommand
from app.application.post_reactions.use_cases.create_post_reaction import CreatePostReactionUseCase
from app.application.post_reactions.use_cases.delete_post_reaction import DeletePostReactionUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.post_reactions.exceptions import PostReactionAlreadyExists, PostReactionNotFound
from app.domain.posts.exceptions import PostNotFoundByIdError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.post_reactions import CreatePostReactionSchema, PostReactionSchema

router = APIRouter(
    prefix='/posts/{post_id}/reactions',
    tags=['Post Reactions'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            'model': PostReactionSchema,
            'description': 'Returns an existing reaction, or updates it if *reaction_type* is different',
        },
        status.HTTP_201_CREATED: {
            'model': PostReactionSchema,
            'description': 'Creates a new reaction',
        },
        status.HTTP_400_BAD_REQUEST: error_response(PostReactionAlreadyExists),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            PostNotFoundByIdError,
            PostReactionNotFound,
        ),
    },
)
async def create_post_reaction(
    post_id: UUID,
    schema: CreatePostReactionSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[CreatePostReactionUseCase],
    response: Response,
) -> PostReactionSchema:
    command = CreatePostReactionCommand(
        current_channel_id=current_channel_id,
        post_id=post_id,
        **schema.model_dump(),
    )
    post_reaction, is_created = await use_case.execute(command=command)
    if is_created:
        response.status_code = status.HTTP_201_CREATED
    return PostReactionSchema.from_entity(entity=post_reaction)


@router.delete(
    path='',
    status_code=status.HTTP_204_NO_CONTENT,
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
            PostReactionNotFound,
        ),
    },
)
async def delete_post_reaction(
    post_id: UUID,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeletePostReactionUseCase],
) -> None:
    command = DeletePostReactionCommand(current_channel_id=current_channel_id, post_id=post_id)
    await use_case.execute(command=command)
