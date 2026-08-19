from abc import ABC, abstractmethod

from app.application.common.commands.email import (
    SendChannelActivationCodeCommand,
    SendChannelResetPasswordCodeCommand,
    SendChannelSetEmailCodeCommand,
)


class ITaskQueue(ABC):
    @abstractmethod
    async def delete_s3_object(self, bucket: str, key: str) -> None: ...

    @abstractmethod
    async def abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> None: ...

    @abstractmethod
    async def send_channel_activation_code(self, command: SendChannelActivationCodeCommand) -> None: ...

    @abstractmethod
    async def send_channel_set_email_code(self, command: SendChannelSetEmailCodeCommand) -> None: ...

    @abstractmethod
    async def send_channel_reset_password_code(self, command: SendChannelResetPasswordCodeCommand) -> None: ...
