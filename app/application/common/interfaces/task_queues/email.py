from abc import ABC, abstractmethod

from app.application.common.commands.email import (
    SendChannelActivationCodeCommand,
    SendChannelResetPasswordCodeCommand,
    SendChannelSetEmailCodeCommand,
)


class IEmailTaskQueue(ABC):
    @abstractmethod
    async def send_channel_activation_code(self, command: SendChannelActivationCodeCommand) -> None: ...

    @abstractmethod
    async def send_channel_set_email_code(self, command: SendChannelSetEmailCodeCommand) -> None: ...

    @abstractmethod
    async def send_channel_reset_password_code(self, command: SendChannelResetPasswordCodeCommand) -> None: ...
