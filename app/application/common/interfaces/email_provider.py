from abc import ABC, abstractmethod


class IEmailProvider(ABC):
    @abstractmethod
    async def send_activation_email(
        self,
        recipients: list[str],
        template_context: dict | None = None,
    ) -> None: ...
