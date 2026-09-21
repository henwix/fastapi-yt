from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.channels.commands import DeleteChannelAvatarCommand, DeleteChannelCommand, UpdateChannelCommand
from app.application.channels.queries import GetChannelAboutInfoQuery, GetChannelQuery
from app.application.channels.usecases import (
    DeleteChannelAvatarUseCase,
    DeleteChannelUseCase,
    GetChannelAboutInfoUseCase,
    GetChannelUseCase,
    UpdateChannelUseCase,
)
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import (
    ChannelAvatarNotFoundError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
    ChannelSlugAlreadyExistsError,
)
from app.domain.common.exceptions.s3 import S3RequestError, S3ResponseError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID
from app.presentation.api.v1.handlers.common.path_params import PathChannelSlug
from app.presentation.api.v1.schemas.requests.channels import UpdateChannelInSchema
from app.presentation.api.v1.schemas.responses.channels import ChannelAboutInfoOutSchema, ChannelOutSchema

router = APIRouter(
    prefix='/channels',
    tags=['Channels'],
    route_class=DishkaRoute,
)


@router.get(
    path='',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def get_channel(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[GetChannelUseCase],
) -> ChannelOutSchema:
    query = GetChannelQuery(current_channel_id=current_channel_id)
    channel = await use_case.execute(query=query)
    return ChannelOutSchema.from_entity(entity=channel)


@router.patch(
    path='',
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
        ),
        status.HTTP_409_CONFLICT: error_response(
            ChannelSlugAlreadyExistsError,
        ),
    },
)
async def update_channel(
    schema: UpdateChannelInSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[UpdateChannelUseCase],
) -> ChannelOutSchema:
    command = UpdateChannelCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(exclude_unset=True),
    )
    channel = await use_case.execute(command=command)
    return ChannelOutSchema.from_entity(entity=channel)


@router.delete(
    path='',
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
        ),
    },
)
async def delete_channel(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeleteChannelUseCase],
) -> None:
    command = DeleteChannelCommand(current_channel_id=current_channel_id)
    await use_case.execute(command=command)


@router.get(
    path='/{channel_slug}/about',
    responses={
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundBySlugError),
    },
)
async def get_channel_about_info(
    channel_slug: PathChannelSlug,
    use_case: FromDishka[GetChannelAboutInfoUseCase],
) -> ChannelAboutInfoOutSchema:
    query = GetChannelAboutInfoQuery(channel_slug=channel_slug)
    channel_about_info_dto = await use_case.execute(query=query)
    return ChannelAboutInfoOutSchema.from_dto(dto=channel_about_info_dto)


@router.delete(
    '/avatar',
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
            ChannelAvatarNotFoundError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def delete_channel_avatar(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeleteChannelAvatarUseCase],
) -> None:
    command = DeleteChannelAvatarCommand(current_channel_id=current_channel_id)
    await use_case.execute(command=command)
