from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.core.configs import BASE_DIR, settings
from app.domain.common.exceptions import EmailSendingError

fm_conf = ConnectionConfig(
    MAIL_USERNAME=settings.email_username,
    MAIL_PASSWORD=settings.email_password,
    MAIL_FROM=settings.email_username,
    MAIL_PORT=587,
    MAIL_SERVER=settings.email_smtp_server,
    MAIL_FROM_NAME=settings.email_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=BASE_DIR / 'app' / 'infrastructure' / 'email' / 'templates',
)


class FastMailClient:
    def __init__(self) -> None:
        self._fm = FastMail(config=fm_conf)

    async def send_email(
        self,
        subject: str,
        recipients: list[str],
        template_name: str,
        template_context: dict | None = None,
    ) -> None:
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                template_body=template_context,
                subtype=MessageType.html,
            )
            await self._fm.send_message(message=message, template_name=template_name)
        except Exception as e:
            raise EmailSendingError(exc_details=str(e)) from e
