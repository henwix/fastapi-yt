from fastapi import Request, status
from starlette.responses import JSONResponse

from app.domain.channels.exceptions import ChannelWithEmailAlreadyExists, ChannelWithSlugAlreadyExists
from app.domain.common.exceptions import AppException


def get_http_status_code(exc: AppException):
    exception_codes: dict[type[AppException], int] = {
        ChannelWithEmailAlreadyExists: status.HTTP_400_BAD_REQUEST,
        ChannelWithSlugAlreadyExists: status.HTTP_400_BAD_REQUEST,
    }
    return exception_codes.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


async def exception_handler(
    _: Request,
    exc: AppException,
) -> JSONResponse:
    return JSONResponse(
        content={'detail': exc.message},
        status_code=get_http_status_code(exc=exc),
    )
