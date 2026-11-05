from dataclasses import dataclass

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class HttpRequestError(AppError):
    message = 'Error occured during HTTP request'
    url: str
    method: str
    error_detail: str


@dataclass(kw_only=True)
class HttpResponseError(AppError):
    message = 'Error occured in HTTP response'
    status_code: int
    url: str
    method: str
    error_detail: str
