from abc import ABC, abstractmethod


class IS3Provider(ABC):
    @abstractmethod
    async def create_multipart_upload(
        self,
        bucket: str,
        filename: str,
        content_type: str,
        key_prefix: str,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]: ...

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
    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[dict],
    ) -> dict: ...

    @abstractmethod
    async def abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> dict: ...

    @abstractmethod
    async def generate_part_upload_url(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int,
    ) -> str: ...

    @abstractmethod
    async def generate_download_url(self, bucket: str, key: str, expires_in: int) -> str: ...

    @abstractmethod
    async def head_object(self, bucket: str, key: str) -> dict: ...

    @abstractmethod
    async def delete_object(self, bucket: str, key: str) -> dict: ...
