from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.channels.commands import (
    ConfirmChannelAvatarUploadCommand,
    CreateChannelCommand,
    DeleteChannelAvatarCommand,
    DeleteChannelCommand,
    GenerateChannelAvatarUploadUrlCommand,
    SetChannelPasswordCommand,
    UpdateChannelCommand,
)
from app.application.channels.queries import GetChannelQuery
from app.application.channels.use_cases.confirm_channel_avatar_upload import ConfirmChannelAvatarUploadUseCase
from app.application.channels.use_cases.create_channel import CreateChannelUseCase
from app.application.channels.use_cases.delete_channel import DeleteChannelUseCase
from app.application.channels.use_cases.delete_channel_avatar import DeleteChannelAvatarUseCase
from app.application.channels.use_cases.generate_channel_avatar_upload_url import GenerateChannelAvatarUploadUrlUseCase
from app.application.channels.use_cases.get_channel import GetChannelUseCase
from app.application.channels.use_cases.set_channel_password import SetChannelPasswordUseCase
from app.application.channels.use_cases.update_channel import UpdateChannelUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidFileContentTypeError,
    ChannelAvatarInvalidFileFormatError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarNotFoundError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
    ChannelWithSlugAlreadyExistsError,
)
from app.domain.common.exceptions import (
    S3ObjectAccessForbiddenError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3UnavailableError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.channels import (
    ChannelAvatarUploadConfirmInSchema,
    ChannelOutSchema,
    CreateChannelInSchema,
    GenerateChannelAvatarUploadUrlInSchema,
    GenerateChannelAvatarUploadUrlOutSchema,
    SetChannelPasswordInSchema,
    UpdateChannelInSchema,
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
    schema: CreateChannelInSchema,
    use_case: FromDishka[CreateChannelUseCase],
) -> ChannelOutSchema:
    command = CreateChannelCommand(**schema.model_dump())
    channel = await use_case.execute(command=command)
    return ChannelOutSchema.from_entity(entity=channel)


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
) -> ChannelOutSchema:
    query = GetChannelQuery(current_channel_id=current_channel_id)
    channel = await use_case.execute(query=query)
    return ChannelOutSchema.from_entity(entity=channel)


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
    schema: UpdateChannelInSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[UpdateChannelUseCase],
) -> ChannelOutSchema:
    command = UpdateChannelCommand(current_channel_id=current_channel_id, **schema.model_dump(exclude_unset=True))
    channel = await use_case.execute(command=command)
    return ChannelOutSchema.from_entity(entity=channel)


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
    schema: SetChannelPasswordInSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[SetChannelPasswordUseCase],
) -> None:
    command = SetChannelPasswordCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/avatar_upload_url',
    status_code=status.HTTP_201_CREATED,
    description='Pass the channel_id in the "x-amz-meta-channel_id" Header to upload the file using upload_url',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(ChannelAvatarInvalidFileFormatError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def generate_avatar_upload_url(
    current_channel_id: CurrentChannelID,
    schema: GenerateChannelAvatarUploadUrlInSchema,
    use_case: FromDishka[GenerateChannelAvatarUploadUrlUseCase],
) -> GenerateChannelAvatarUploadUrlOutSchema:
    command = GenerateChannelAvatarUploadUrlCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    url, key, channel_id = await use_case.execute(command=command)
    return GenerateChannelAvatarUploadUrlOutSchema(
        upload_url=url,
        key=key,
        channel_id=channel_id,
    )


@router.post(
    '/avatar_upload_confirm',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelAvatarInvalidFileFormatError,
            ChannelAvatarInvalidKeyError,
            ChannelAvatarAlreadySetError,
            ChannelAvatarInvalidFileContentTypeError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError, S3ObjectAccessForbiddenError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError, S3ObjectNotFoundError),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def avatar_upload_confirm(
    current_channel_id: CurrentChannelID,
    schema: ChannelAvatarUploadConfirmInSchema,
    use_case: FromDishka[ConfirmChannelAvatarUploadUseCase],
) -> None:
    command = ConfirmChannelAvatarUploadCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)


@router.delete(
    '/avatar_delete',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError, ChannelAvatarNotFoundError),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def delete_avatar(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[DeleteChannelAvatarUseCase],
) -> None:
    command = DeleteChannelAvatarCommand(current_channel_id=current_channel_id)
    await use_case.execute(command=command)
