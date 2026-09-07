from dataclasses import dataclass

from app.domain.common.exceptions.base import AppException


@dataclass(kw_only=True)
class HttpRequestError(AppException):
    message = 'Error occured during HTTP request'
    url: str
    method: str
    exc_details: str


@dataclass(kw_only=True)
class HttpResponseError(AppException):
    message = 'Error occured in HTTP response'
    status_code: int
    url: str
    method: str
    exc_details: str
