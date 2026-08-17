from abc import ABC, abstractmethod


class ITaskQueue(ABC):
    @abstractmethod
    async def delete_s3_object(self, bucket: str, key: str) -> None: ...

    @abstractmethod
    async def abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> None: ...

    @abstractmethod
    async def send_channel_activation_code(
        self, recipients: list[str], template_context: dict | None = None
    ) -> None: ...

    @abstractmethod
    async def send_channel_set_email_code(
        self, recipients: list[str], template_context: dict | None = None
    ) -> None: ...

    @abstractmethod
    async def send_channel_reset_password_code(
        self, recipients: list[str], template_context: dict | None = None
    ) -> None: ...
