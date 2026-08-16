from dataclasses import dataclass

from app.application.common.interfaces.email_provider import IEmailProvider
from app.infrastructure.email.client import FastMailClient


@dataclass
class FastMailProvider(IEmailProvider):
    _smtp_client: FastMailClient

    async def send_activation_email(
        self,
        recipients: list[str],
        template_context: dict | None = None,
    ) -> None:
        await self._smtp_client.send_email(
            subject='Account activation',
            recipients=recipients,
            template_name='activation.html',
            template_context=template_context,
        )
