from abc import ABC, abstractmethod


class IEmailProvider(ABC):
    @abstractmethod
    async def send_channel_activation_code(
        self,
        recipients: list[str],
        template_context: dict | None = None,
    ) -> None: ...

    @abstractmethod
    async def send_channel_set_email_code(
        self,
        recipients: list[str],
        template_context: dict | None = None,
    ) -> None: ...

    @abstractmethod
    async def send_channel_reset_password_code(
        self,
        recipients: list[str],
        template_context: dict | None = None,
    ) -> None: ...
