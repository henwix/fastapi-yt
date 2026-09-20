from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.channels.commands import (
    ConfirmChannelAvatarUploadCommand,
    GenerateChannelAvatarUploadUrlCommand,
)
from app.application.channels.usecases import (
    ConfirmChannelAvatarUploadUseCase,
    GenerateChannelAvatarUploadUrlUseCase,
)
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidContentTypeError,
    ChannelAvatarInvalidFilenameError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarSizeTooBigError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from app.domain.common.exceptions.s3 import (
    S3ObjectAccessForbiddenError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3ResponseError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID
from app.presentation.api.v1.schemas.requests.channels import (
    ChannelAvatarUploadConfirmInSchema,
    GenerateChannelAvatarUploadUrlInSchema,
)
from app.presentation.api.v1.schemas.responses.channels import GenerateChannelAvatarUploadUrlOutSchema

router = APIRouter(
    prefix='/channels',
    tags=['Channel Uploads'],
    route_class=DishkaRoute,
)


@router.post(
    path='/avatar_upload_url',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelAvatarInvalidFilenameError,
        ),
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
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def generate_channel_avatar_upload_url(
    current_channel_id: CurrentChannelID,
    schema: GenerateChannelAvatarUploadUrlInSchema,
    use_case: FromDishka[GenerateChannelAvatarUploadUrlUseCase],
) -> GenerateChannelAvatarUploadUrlOutSchema:
    """
    Allowed mime types for Channel Avatar file:
    - **.png**
    - **.jpg**
    - **.jpeg**
    - **.webp**

    After the URL is generated, pass the **channel_id** in the *"x-amz-meta-channel_id"* header to upload the file
    using **upload_url**
    """
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
            ChannelAvatarInvalidKeyError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError, S3ObjectAccessForbiddenError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError, S3ObjectNotFoundError),
        status.HTTP_409_CONFLICT: error_response(
            ChannelAvatarAlreadySetError,
            ChannelAvatarInvalidContentTypeError,
            ChannelAvatarSizeTooBigError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def channel_avatar_upload_confirm(
    current_channel_id: CurrentChannelID,
    schema: ChannelAvatarUploadConfirmInSchema,
    use_case: FromDishka[ConfirmChannelAvatarUploadUseCase],
) -> None:
    command = ConfirmChannelAvatarUploadCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)
