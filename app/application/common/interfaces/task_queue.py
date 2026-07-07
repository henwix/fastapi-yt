from abc import ABC, abstractmethod


class ITaskQueue(ABC):
    @abstractmethod
    async def delete_s3_object(self, bucket: str, key: str) -> None: ...
