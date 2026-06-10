from dataclasses import dataclass

from app.domain.common.exceptions import AppException


@dataclass
class ChannelWithSlugAlreadyExists(AppException):
    message = 'Channel with this slug already exists'
    slug: str


@dataclass
class ChannelWithEmailAlreadyExists(AppException):
    message = 'Channel with this email already exists'
    email: str


@dataclass
class ChannelNotFoundError(AppException):
    message = 'Channel not found'


@dataclass(kw_only=True)
class ChannelNotFoundBySlugError(AppException):
    message = 'Channel not found by slug'

    slug: str


@dataclass
class ChannelNotActiveError(AppException):
    message = 'Channel not active'
