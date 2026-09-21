from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from httpx import AsyncClient
from types_aiobotocore_s3.client import S3Client

from app.application.common.interfaces.email import IEmailProvider, IEmailService
from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.http_client import IHttpClient
from app.application.common.interfaces.s3 import IS3Provider, IS3Service
from app.application.common.interfaces.security import IPasswordHasher
from app.infrastructure.email.client import FastMailClient
from app.infrastructure.email.provider import FastMailProvider
from app.infrastructure.email.service import EmailService
from app.infrastructure.files.file_type_detector import FileTypeDetector
from app.infrastructure.http.client import HttpxClient
from app.infrastructure.http.config import get_httpx_client
from app.infrastructure.s3.config import get_s3_client
from app.infrastructure.s3.provider import BotoS3Provider
from app.infrastructure.s3.service import S3Service
from app.infrastructure.security.password_hasher import PwdlibPasswordHasher


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    async def provide_httpx_async_client(self) -> AsyncGenerator[AsyncClient]:
        client = get_httpx_client()
        yield client
        await client.aclose()

    @provide(scope=Scope.APP)
    async def provide_s3_async_client(self) -> AsyncGenerator[S3Client]:
        async with get_s3_client() as s3_client:
            yield s3_client

    http_client = provide(HttpxClient, scope=Scope.REQUEST, provides=IHttpClient)
    file_type_detector = provide(FileTypeDetector, scope=Scope.REQUEST, provides=IFileTypeDetector)
    s3_provider = provide(BotoS3Provider, scope=Scope.REQUEST, provides=IS3Provider)
    s3_service = provide(S3Service, scope=Scope.REQUEST, provides=IS3Service)
    smtp_client = provide(FastMailClient, scope=Scope.APP)
    email_provider = provide(FastMailProvider, scope=Scope.REQUEST, provides=IEmailProvider)
    email_service = provide(EmailService, scope=Scope.REQUEST, provides=IEmailService)
    password_hasher = provide(PwdlibPasswordHasher, scope=Scope.APP, provides=IPasswordHasher)
