from dataclasses import dataclass


@dataclass
class AppException(Exception):
    message = 'Application exception occured'


@dataclass
class InvalidCursorError(AppException):
    message = 'Invalid cursor value'
    cursor: str
