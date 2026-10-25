from dataclasses import asdict
from logging import getLogger
from types import MappingProxyType

from fastapi import FastAPI, Request, status

from app.domain.common.exceptions.base import AppError
from app.presentation.api.exceptions.auth import init_auth
from app.presentation.api.exceptions.channels import init_channels
from app.presentation.api.exceptions.common import init_common
from app.presentation.api.exceptions.oauth import init_oauth
from app.presentation.api.exceptions.playlists import init_playlists
from app.presentation.api.exceptions.posts import init_posts
from app.presentation.api.exceptions.subscriptions import init_subscriptions
from app.presentation.api.exceptions.videos import init_videos
from app.presentation.api.responses.msgspec import MsgSpecJSONResponse

logger = getLogger(__name__)


class ExceptionHandler:
    EXCEPTION_CODES: MappingProxyType[type[AppError], int] = MappingProxyType(
        {
            **init_common(),
            **init_channels(),
            **init_auth(),
            **init_oauth(),
            **init_videos(),
            **init_playlists(),
            **init_posts(),
            **init_subscriptions(),
        }
    )

    def _get_exceptions_chain(self, exc: AppError) -> list:
        exceptions = []

        current_exc: BaseException | None = exc.__cause__

        while current_exc is not None:
            if not isinstance(current_exc, AppError):
                break

            exc_data = {
                'name': type(current_exc).__name__,
                'message': current_exc.message,
                'meta': asdict(current_exc),
            }
            exceptions.append(exc_data)
            current_exc = current_exc.__cause__

        return exceptions

    async def _handle(self, _: Request, exc: AppError) -> MsgSpecJSONResponse:
        logger.error(
            msg=exc.message,
            extra={
                'log_meta': asdict(exc),
                'exceptions': self._get_exceptions_chain(exc=exc),
            },
        )
        return MsgSpecJSONResponse(
            content={'detail': exc.message},
            status_code=self.EXCEPTION_CODES.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR),
        )

    def setup_handler(self, app: FastAPI) -> None:
        app.add_exception_handler(AppError, self._handle)
