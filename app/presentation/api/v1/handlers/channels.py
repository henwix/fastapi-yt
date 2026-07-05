from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.channels.commands import (
    ConfirmChannelAvatarUploadCommand,
    CreateChannelCommand,
    DeleteChannelCommand,
    GenerateChannelAvatarUploadURLCommand,
    SetChannelPasswordCommand,
    UpdateChannelCommand,
)
from app.application.channels.queries import GetChannelQuery
from app.application.channels.use_cases.confirm_channel_avatar_upload import ChannelAvatarUploadConfirmUseCase
from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.application.channels.use_cases.generate_channel_avatar_upload_url import GenerateChannelAvatarUploadURLUseCase
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.application.channels.use_cases.set_password import SetChannelPasswordUseCase
from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import (
    ChannelAvatarInvalidFormatError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
    ChannelWithSlugAlreadyExistsError,
)
from app.domain.common.exceptions import (
    S3FileAccessForbiddenError,
    S3FileNotFoundError,
    S3RequestError,
    S3UnavailableError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.channels import (
    ChannelAvatarUploadConfirmSchema,
    ChannelSchema,
    CreateChannelSchema,
    GenerateChannelAvatarUploadURLInSchema,
    GenerateChannelAvatarUploadURLOutSchema,
    SetChannelPasswordSchema,
    UpdateChannelSchema,
)

router = APIRouter(
    prefix='/channels',
    tags=['Channels'],
    route_class=DishkaRoute,
)


@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelWithEmailAlreadyExistsError,
            ChannelWithSlugAlreadyExistsError,
        )
    },
)
async def create_channel(
    schema: CreateChannelSchema,
    use_case: FromDishka[CreateChannelUseCase],
) -> ChannelSchema:
    command = CreateChannelCommand(**schema.model_dump())
    channel = await use_case.execute(command=command)
    return ChannelSchema.from_entity(entity=channel)


@router.get(
    path='',
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
async def get_channel(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[GetChannelUseCase],
) -> ChannelSchema:
    query = GetChannelQuery(current_channel_id=current_channel_id)
    channel = await use_case.execute(query=query)
    return ChannelSchema.from_entity(entity=channel)


@router.patch(
    path='',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(ChannelWithSlugAlreadyExistsError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
    },
)
async def update_channel(
    schema: UpdateChannelSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[UpdateChannelUseCase],
) -> ChannelSchema:
    command = UpdateChannelCommand(current_channel_id=current_channel_id, **schema.model_dump(exclude_unset=True))
    channel = await use_case.execute(command=command)
    return ChannelSchema.from_entity(entity=channel)


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
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
    },
)
async def delete_channel(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeleteChannelUseCase],
) -> None:
    command = DeleteChannelCommand(current_channel_id=current_channel_id)
    await use_case.execute(command=command)


@router.post(
    path='/set_password',
    status_code=status.HTTP_204_NO_CONTENT,
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
async def set_password(
    schema: SetChannelPasswordSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[SetChannelPasswordUseCase],
) -> None:
    command = SetChannelPasswordCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/avatar_upload_url',
    status_code=status.HTTP_201_CREATED,
    description='Pass the channel_id in the "x-amz-meta-user_id" Header to upload the file using upload_url',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(ChannelAvatarInvalidFormatError),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
    },
)
async def generate_avatar_upload_url(
    current_channel_id: CurrentChannelID,
    schema: GenerateChannelAvatarUploadURLInSchema,
    use_case: FromDishka[GenerateChannelAvatarUploadURLUseCase],
) -> GenerateChannelAvatarUploadURLOutSchema:
    command = GenerateChannelAvatarUploadURLCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    url, key, channel_id = await use_case.execute(command=command)
    return GenerateChannelAvatarUploadURLOutSchema(
        upload_url=url,
        key=key,
        channel_id=channel_id,
    )


@router.post(
    '/avatar_upload_confirm',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError, S3FileAccessForbiddenError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError, S3FileNotFoundError),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def avatar_upload_confirm(
    current_channel_id: CurrentChannelID,
    schema: ChannelAvatarUploadConfirmSchema,
    use_case: FromDishka[ChannelAvatarUploadConfirmUseCase],
) -> None:
    command = ConfirmChannelAvatarUploadCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)
