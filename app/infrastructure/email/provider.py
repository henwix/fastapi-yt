from dataclasses import dataclass

from app.application.common.interfaces.email_provider import IEmailProvider
from app.infrastructure.email.client import FastMailClient


@dataclass
class FastMailProvider(IEmailProvider):
    _smtp_client: FastMailClient

    async def send_channel_activation_code(
        self,
        recipient: str,
        template_context: dict | None = None,
    ) -> None:
        await self._smtp_client.send_email(
            subject='Confirm channel activation',
            recipients=[recipient],
            template_name='channel_activation.html',
            template_context=template_context,
        )

    async def send_channel_set_email_code(
        self,
        recipient: str,
        template_context: dict | None = None,
    ) -> None:
        await self._smtp_client.send_email(
            subject='Confirm the email address you want to set',
            recipients=[recipient],
            template_name='channel_set_email_confirmation.html',
            template_context=template_context,
        )

    async def send_channel_reset_password_code(
        self,
        recipient: str,
        template_context: dict | None = None,
    ) -> None:
        await self._smtp_client.send_email(
            subject='Confirm the password you want to set',
            recipients=[recipient],
            template_name='channel_reset_password_confirmation.html',
            template_context=template_context,
        )
