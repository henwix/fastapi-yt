from dataclasses import dataclass

from aioboto3 import Session

from app.application.common.interfaces.s3_client import IS3Client
from app.core.configs import settings


@dataclass
class BotoS3Client(IS3Client):
    _session: Session

    def client(self):
        return self._session.client(
            service_name='s3',
            region_name='auto',
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
