from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Path, status

from app.application.videos.commands import (
    AbortVideoMultipartUploadCommand,
    CompleteVideoMultipartUploadCommand,
    CreateVideoMultipartUploadCommand,
    DeleteVideoCommand,
    GenerateVideoDownloadUrlCommand,
    GenerateVideoPartUploadUrlCommand,
    GetVideoCommand,
    UpdateVideoCommand,
)
from app.application.videos.use_cases.abort_video_multipart_upload import AbortVideoMultipartUploadUseCase
from app.application.videos.use_cases.complete_video_multipart_upload import CompleteVideoMultipartUploadUseCase
from app.application.videos.use_cases.create_video_multipart_upload import CreateVideoMultipartUploadUseCase
from app.application.videos.use_cases.delete_video import DeleteVideoUseCase
from app.application.videos.use_cases.generate_video_download_url import GenerateVideoDownloadUrlUseCase
from app.application.videos.use_cases.generate_video_part_upload_url import GenerateVideoPartUploadUrlUseCase
from app.application.videos.use_cases.get_video import GetVideoUseCase
from app.application.videos.use_cases.update_video import UpdateVideoUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.exceptions import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3RequestError,
    S3UnavailableError,
)
from app.domain.videos.constants import VIDEO_ID_PATTERN
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileFormatError,
    VideoInvalidKeyError,
    VideoNotFoundByIdError,
    VideoNotFoundByUploadIdAndS3KeyError,
    VideoUploadAlreadyCompletedError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.schemas.common import CompleteMultipartUploadInSchema
from app.presentation.api.v1.schemas.videos import (
    AbortVideoMultipartUploadInSchema,
    CreateVideoMultipartUploadInSchema,
    CreateVideoMultipartUploadOutSchema,
    DetailedVideoOutSchema,
    GenerateVideoDownloadUrlOutSchema,
    GenerateVideoPartUploadUrlInSchema,
    GenerateVideoPartUploadUrlOutSchema,
    UpdateVideoInSchema,
    VideoOutSchema,
)

router = APIRouter(
    prefix='/videos',
    tags=['Videos'],
    route_class=DishkaRoute,
)

PathVideoId = Annotated[str, Path(pattern=VIDEO_ID_PATTERN)]


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
) -> CreateVideoMultipartUploadOutSchema:
    command = CreateVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    video = await use_case.execute(command=command)
    return CreateVideoMultipartUploadOutSchema.from_entity(entity=video)


@router.post(
    '/part_upload_url',
    summary='Generate Part Upload Url For Multipart Upload',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoInvalidFileFormatError,
            VideoInvalidKeyError,
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
            VideoNotFoundByUploadIdAndS3KeyError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def generate_part_upload_url(
    current_channel_id: CurrentChannelID,
    schema: GenerateVideoPartUploadUrlInSchema,
    use_case: FromDishka[GenerateVideoPartUploadUrlUseCase],
) -> GenerateVideoPartUploadUrlOutSchema:
    command = GenerateVideoPartUploadUrlCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    upload_url = await use_case.execute(command=command)
    return GenerateVideoPartUploadUrlOutSchema(upload_url=upload_url)


@router.post(
    path='/complete_multipart_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoInvalidFileFormatError,
            VideoInvalidKeyError,
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
            VideoNotFoundByUploadIdAndS3KeyError,
            VideoNotFoundByIdError,
            S3MultipartUploadNotFoundError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def complete_multipart_upload(
    current_channel_id: CurrentChannelID,
    schema: CompleteMultipartUploadInSchema,
    use_case: FromDishka[CompleteVideoMultipartUploadUseCase],
):
    command = CompleteVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    await use_case.execute(command=command)


@router.post(
    path='/abort_multipart_upload',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            VideoInvalidFileFormatError,
            VideoInvalidKeyError,
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
            VideoNotFoundByUploadIdAndS3KeyError,
            VideoNotFoundByIdError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(S3RequestError, S3UnavailableError),
    },
)
async def abort_multipart_upload(
    current_channel_id: CurrentChannelID,
    schema: AbortVideoMultipartUploadInSchema,
    use_case: FromDishka[AbortVideoMultipartUploadUseCase],
) -> None:
    command = AbortVideoMultipartUploadCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
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
            VideoNotFoundByIdError,
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


@router.delete(
    path='/{video_id}',
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
            VideoNotFoundByIdError,
        ),
    },
)
async def delete_video(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[DeleteVideoUseCase],
) -> None:
    command = DeleteVideoCommand(current_channel_id=current_channel_id, video_id=video_id)
    await use_case.execute(command=command)


@router.get(
    path='/{video_id}',
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
            VideoNotFoundByIdError,
        ),
    },
)
async def get_video(
    current_channel_id: OptionalCurrentChannelID,
    video_id: PathVideoId,
    use_case: FromDishka[GetVideoUseCase],
) -> DetailedVideoOutSchema:
    command = GetVideoCommand(current_channel_id=current_channel_id, video_id=video_id)
    video = await use_case.execute(command=command)
    return DetailedVideoOutSchema.from_dto(dto=video)


@router.patch(
    path='/{video_id}',
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
            VideoNotFoundByIdError,
        ),
    },
)
async def update_video(
    current_channel_id: CurrentChannelID,
    video_id: PathVideoId,
    schema: UpdateVideoInSchema,
    use_case: FromDishka[UpdateVideoUseCase],
) -> VideoOutSchema:
    command = UpdateVideoCommand(
        current_channel_id=current_channel_id,
        video_id=video_id,
        **schema.model_dump(exclude_unset=True),
    )
    video = await use_case.execute(command=command)
    return VideoOutSchema.from_entity(entity=video)
