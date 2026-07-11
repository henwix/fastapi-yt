from abc import ABC, abstractmethod


class ITaskQueue(ABC):
    @abstractmethod
    async def delete_s3_object(self, bucket: str, key: str) -> None: ...

    @abstractmethod
    async def abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> None: ...
