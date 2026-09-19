from fastapi import status

from app.domain.channels.exceptions import (
    ChannelActivationFailedError,
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidContentTypeError,
    ChannelAvatarInvalidFilenameError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarNotFoundError,
    ChannelAvatarSizeTooBigError,
    ChannelEmailAlreadyExistsError,
    ChannelEmailInvalidFormatError,
    ChannelEmailTooLongError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
    ChannelSlugAlreadyExistsError,
    ChannelSlugInvalidFormatError,
)
from app.domain.common.exceptions.base import AppError


def init_channels() -> dict[type[AppError], int]:
    return {
        ChannelEmailAlreadyExistsError: status.HTTP_409_CONFLICT,
        ChannelEmailInvalidFormatError: status.HTTP_400_BAD_REQUEST,
        ChannelEmailTooLongError: status.HTTP_400_BAD_REQUEST,
        ChannelSlugAlreadyExistsError: status.HTTP_409_CONFLICT,
        ChannelSlugInvalidFormatError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidKeyError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidFilenameError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidContentTypeError: status.HTTP_409_CONFLICT,
        ChannelAvatarSizeTooBigError: status.HTTP_409_CONFLICT,
        ChannelAvatarAlreadySetError: status.HTTP_409_CONFLICT,
        ChannelActivationFailedError: status.HTTP_409_CONFLICT,
        ChannelNotActiveError: status.HTTP_403_FORBIDDEN,
        ChannelNotFoundByIdError: status.HTTP_404_NOT_FOUND,
        ChannelNotFoundBySlugError: status.HTTP_404_NOT_FOUND,
        ChannelAvatarNotFoundError: status.HTTP_404_NOT_FOUND,
    }
