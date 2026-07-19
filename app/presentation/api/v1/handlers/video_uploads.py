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
from app.domain.common.exceptions import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3RequestError,
    S3UnavailableError,
)
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileFormatError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.handlers.common.params import PathVideoId
from app.presentation.api.v1.schemas.common import CompleteMultipartUploadInSchema
from app.presentation.api.v1.schemas.videos import (
    CreateVideoMultipartUploadInSchema,
    GenerateVideoDownloadUrlOutSchema,
    GenerateVideoPartUploadUrlOutSchema,
    VideoOutSchema,
)

router = APIRouter(
    prefix='/videos',
    tags=['Video Uploads'],
    route_class=DishkaRoute,
)


@router.post(
    path='/create_multipart_upload',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(VideoInvalidFileFormatError),
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
async def create_mutipart_upload(
    current_channel_id: CurrentChannelID,
    schema: CreateVideoMultipartUploadInSchema,
    use_case: FromDishka[CreateVideoMultipartUploadUseCase],
) -> VideoOutSchema:
    command = CreateVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    video = await use_case.execute(command=command)
    return VideoOutSchema.from_entity(entity=video)


@router.get(
    '/{video_id}/part_upload_url',
    summary='Generate Part Upload Url For Multipart Upload',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoUploadAlreadyCompletedError,
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
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def generate_part_upload_url(
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
    path='/{video_id}/complete_multipart_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoUploadAlreadyCompletedError,
            S3MultipartUploadInvalidPartsError,
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
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def complete_multipart_upload(
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
    path='/{video_id}/abort_multipart_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Abort Multipart Upload And Delete Video',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoUploadAlreadyCompletedError,
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
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def abort_multipart_upload(
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
async def generate_download_url(
    current_channel_id: OptionalCurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[GenerateVideoDownloadUrlUseCase],
) -> GenerateVideoDownloadUrlOutSchema:
    command = GenerateVideoDownloadUrlCommand(current_channel_id=current_channel_id, video_id=video_id)
    download_url = await use_case.execute(command=command)
    return GenerateVideoDownloadUrlOutSchema(download_url=download_url)
