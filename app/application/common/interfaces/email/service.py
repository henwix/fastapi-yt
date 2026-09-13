from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def schedule_send_channel_activation_code(
        self, email: str, name: str, activation_url: str, code: str
    ) -> None: ...

    @abstractmethod
    async def schedule_send_channel_set_email_code(
        self, email: str, name: str, confirmation_url: str, code: str
    ) -> None: ...

    @abstractmethod
    async def schedule_send_channel_reset_password_code(
        self, email: str, name: str, confirmation_url: str, code: str, uid: str
    ) -> None: ...
