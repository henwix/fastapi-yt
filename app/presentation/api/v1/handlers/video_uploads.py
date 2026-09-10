from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Query, status

from app.application.videos.commands import (
    AbortVideoMultipartUploadCommand,
    CompleteVideoMultipartUploadCommand,
    CreateVideoMultipartUploadCommand,
    GenerateVideoDownloadUrlCommand,
    GenerateVideoPartUploadUrlCommand,
)
from app.application.videos.use_cases.abort_video_multipart_upload import AbortVideoMultipartUploadUseCase
from app.application.videos.use_cases.complete_video_multipart_upload import CompleteVideoMultipartUploadUseCase
from app.application.videos.use_cases.create_video_multipart_upload import CreateVideoMultipartUploadUseCase
from app.application.videos.use_cases.generate_video_download_url import GenerateVideoDownloadUrlUseCase
from app.application.videos.use_cases.generate_video_part_upload_url import GenerateVideoPartUploadUrlUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions.s3 import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3RequestError,
    S3ResponseError,
)
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileContentTypeError,
    VideoInvalidFileFormatError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
    VideoUploadAlreadyCreatedError,
    VideoUploadNotCreatedError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.requests.common import CompleteMultipartUploadInSchema
from app.presentation.api.v1.schemas.requests.videos import CreateVideoMultipartUploadInSchema
from app.presentation.api.v1.schemas.responses.videos import (
    GenerateVideoDownloadUrlOutSchema,
    GenerateVideoPartUploadUrlOutSchema,
)

router = APIRouter(
    prefix='/videos',
    tags=['Video Uploads'],
    route_class=DishkaRoute,
)


@router.post(
    path='/{video_id}/create_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(VideoInvalidFileFormatError),
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
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadAlreadyCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            S3ResponseError,
            S3RequestError,
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
    '/{video_id}/part_upload_url',
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
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadNotCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3ResponseError, S3RequestError),
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
    path='/{video_id}/complete_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            S3MultipartUploadInvalidPartsError,
            VideoInvalidFileContentTypeError,
        ),
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
            S3MultipartUploadNotFoundError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadNotCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3ResponseError, S3RequestError),
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
    path='/{video_id}/abort_upload',
    status_code=status.HTTP_204_NO_CONTENT,
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
        ),
        status.HTTP_409_CONFLICT: error_response(
            VideoUploadAlreadyCompletedError,
            VideoUploadNotCreatedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3ResponseError, S3RequestError),
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


@router.get(
    path='/{video_id}/download_url',
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
