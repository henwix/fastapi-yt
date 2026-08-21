from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.application.common.commands.s3 import AbortMultipartUploadCommand, DeleteS3ObjectCommand


@dataclass
class IS3TaskQueue(ABC):
    @abstractmethod
    async def delete_s3_object(self, command: DeleteS3ObjectCommand) -> None: ...

    @abstractmethod
    async def abort_multipart_upload(self, command: AbortMultipartUploadCommand) -> None: ...
