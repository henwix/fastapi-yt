from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status

from app.application.videos.commands import (
    AbortVideoMultipartUploadCommand,
    CompleteVideoMultipartUploadCommand,
    ConfirmVideoThumbnailUploadCommand,
    CreateVideoMultipartUploadCommand,
    DeleteVideoThumbnailCommand,
    GenerateVideoDownloadUrlCommand,
    GenerateVideoPartUploadUrlCommand,
    GenerateVideoThumbnailUploadUrlCommand,
)
from app.application.videos.use_cases.abort_video_multipart_upload import AbortVideoMultipartUploadUseCase
from app.application.videos.use_cases.complete_video_multipart_upload import CompleteVideoMultipartUploadUseCase
from app.application.videos.use_cases.confirm_video_thumbnail_upload import ConfirmVideoThumbnailUploadUseCase
from app.application.videos.use_cases.create_video_multipart_upload import CreateVideoMultipartUploadUseCase
from app.application.videos.use_cases.delete_video_thumbnail import DeleteVideoThumbnailUseCase
from app.application.videos.use_cases.generate_video_download_url import GenerateVideoDownloadUrlUseCase
from app.application.videos.use_cases.generate_video_part_upload_url import GenerateVideoPartUploadUrlUseCase
from app.application.videos.use_cases.generate_video_thumbnail_upload_url import GenerateVideoThumbnailUploadUrlUseCase
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions.s3 import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3ObjectAccessForbiddenError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3ResponseError,
)
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileContentTypeError,
    VideoInvalidFilenameError,
    VideoNotFoundError,
    VideoThumbnailAlreadySetError,
    VideoThumbnailInvalidContentTypeError,
    VideoThumbnailInvalidFilenameError,
    VideoThumbnailInvalidKeyError,
    VideoThumbnailNotFoundError,
    VideoThumbnailSizeTooBigError,
    VideoThumbnailVideoIdMismatchError,
    VideoUploadAlreadyCompletedError,
    VideoUploadAlreadyCreatedError,
    VideoUploadNotCreatedError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.requests.common import CompleteMultipartUploadInSchema
from app.presentation.api.v1.schemas.requests.videos import (
    ConfirmVideoThumbnailUploadInSchema,
    CreateVideoMultipartUploadInSchema,
    GenerateVideoThumbnailUploadUrlInSchema,
)
from app.presentation.api.v1.schemas.responses.videos import (
    GenerateVideoDownloadUrlOutSchema,
    GenerateVideoPartUploadUrlOutSchema,
    GenerateVideoThumbnailUploadUrlOutSchema,
)

router = APIRouter(
    prefix='/videos/{video_id}',
    tags=['Video Uploads'],
    route_class=DishkaRoute,
)


@router.post(
    path='/create_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(VideoInvalidFilenameError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadAlreadyCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def create_video_mutipart_upload(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: CreateVideoMultipartUploadInSchema,
    use_case: FromDishka[CreateVideoMultipartUploadUseCase],
) -> None:
    command = CreateVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(),
    )
    await use_case.execute(command=command)


@router.get(
    '/part_upload_url',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadNotCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def generate_video_part_upload_url(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    part_number: Annotated[int, Query(ge=1, le=10000)],
    use_case: FromDishka[GenerateVideoPartUploadUrlUseCase],
) -> GenerateVideoPartUploadUrlOutSchema:
    command = GenerateVideoPartUploadUrlCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        part_number=part_number,
    )
    upload_url = await use_case.execute(command=command)
    return GenerateVideoPartUploadUrlOutSchema(upload_url=upload_url)


@router.post(
    path='/complete_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            S3MultipartUploadInvalidPartsError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
            S3MultipartUploadNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadNotCreatedError,
            VideoInvalidFileContentTypeError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def complete_video_multipart_upload(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: CompleteMultipartUploadInSchema,
    use_case: FromDishka[CompleteVideoMultipartUploadUseCase],
):
    command = CompleteVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(),
    )
    await use_case.execute(command=command)


@router.delete(
    path='/abort_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadNotCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3RequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            S3ResponseError,
        ),
    },
)
async def abort_video_multipart_upload(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[AbortVideoMultipartUploadUseCase],
) -> None:
    command = AbortVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
    )
    await use_case.execute(command=command)


@router.post(
    path='/thumbnail_upload_url',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoThumbnailInvalidFilenameError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
    },
)
async def generate_video_thumbnail_upload_url(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: GenerateVideoThumbnailUploadUrlInSchema,
    use_case: FromDishka[GenerateVideoThumbnailUploadUrlUseCase],
) -> GenerateVideoThumbnailUploadUrlOutSchema:
    """
    Pass the channel_id in the "x-amz-meta-channel_id" and video_id in the "x-amz-meta-video_id" headers to
    upload the file using upload_url
    """
    command = GenerateVideoThumbnailUploadUrlCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(),
    )
    url, key, channel_id, video_id = await use_case.execute(command=command)
    return GenerateVideoThumbnailUploadUrlOutSchema(upload_url=url, key=key, channel_id=channel_id, video_id=video_id)


@router.post(
    '/thumbnail_upload_confirm',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoThumbnailInvalidKeyError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
            S3ObjectAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
            S3ObjectNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoThumbnailAlreadySetError,
            VideoThumbnailVideoIdMismatchError,
            VideoThumbnailSizeTooBigError,
            VideoThumbnailInvalidContentTypeError,
        ),
    },
)
async def video_thumbnail_upload_confirm(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: ConfirmVideoThumbnailUploadInSchema,
    use_case: FromDishka[ConfirmVideoThumbnailUploadUseCase],
) -> None:
    command = ConfirmVideoThumbnailUploadCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(),
    )
    await use_case.execute(command=command)


@router.delete(
    path='/thumbnail_delete',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
            VideoThumbnailNotFoundError,
        ),
    },
)
async def delete_video_thumbnail(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[DeleteVideoThumbnailUseCase],
) -> None:
    command = DeleteVideoThumbnailCommand(current_channel_id=current_channel_id, video_id=video_id)
    await use_case.execute(command=command)


@router.get(
    path='/download_url',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
            VideoAccessForbiddenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            VideoNotFoundError,
        ),
    },
)
async def generate_video_download_url(
    current_channel_id: OptionalCurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[GenerateVideoDownloadUrlUseCase],
) -> GenerateVideoDownloadUrlOutSchema:
    command = GenerateVideoDownloadUrlCommand(current_channel_id=current_channel_id, video_id=video_id)
    download_url = await use_case.execute(command=command)
    return GenerateVideoDownloadUrlOutSchema(download_url=download_url)
