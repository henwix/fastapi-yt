from dataclasses import asdict
from logging import getLogger

from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.interfaces.email_provider import IEmailProvider
from app.domain.common.exceptions import AppException
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()
logger = getLogger(__name__)


@broker.task(task_name='send_activation_email_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_activation_email_task(
    email_provider: FromDishka[IEmailProvider],
    recipients: list[str],
    template_context: dict | None = None,
) -> None:
    logger.info('Start email activation sending', extra={'log_meta': {'recipients': recipients}})
    try:
        await email_provider.send_activation_email(recipients=recipients, template_context=template_context)
    except AppException as e:
        logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
        raise
    logger.info('Complete email activation sending', extra={'log_meta': {'recipients': recipients}})
