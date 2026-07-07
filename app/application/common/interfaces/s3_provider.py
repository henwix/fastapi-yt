from abc import ABC, abstractmethod


class IS3Provider(ABC):
    @abstractmethod
    async def generate_upload_url(
        self,
        bucket: str,
        filename: str,
        content_type: str,
        key_prefix: str,
        expires_in: int,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]: ...

    @abstractmethod
    async def get_object(self, bucket: str, key: str) -> dict: ...

    @abstractmethod
    async def head_object(self, bucket: str, key: str) -> dict: ...

    @abstractmethod
    async def delete_object(self, bucket: str, key: str) -> dict: ...
