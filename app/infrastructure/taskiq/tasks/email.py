from dataclasses import asdict
from logging import getLogger

from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.interfaces.email_provider import IEmailProvider
from app.domain.common.exceptions import AppException
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()
logger = getLogger(__name__)


@broker.task(task_name='send_channel_activation_code_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_channel_activation_code_task(
    email_provider: FromDishka[IEmailProvider],
    recipients: list[str],
    template_context: dict | None = None,
) -> None:
    logger.info('Start channel activation code sending', extra={'log_meta': {'recipients': recipients}})
    try:
        await email_provider.send_channel_activation_code(recipients=recipients, template_context=template_context)
    except AppException as e:
        logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
        raise
    logger.info('Complete channel activation code sending', extra={'log_meta': {'recipients': recipients}})


@broker.task(task_name='send_channel_set_email_code_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_channel_set_email_code_task(
    email_provider: FromDishka[IEmailProvider],
    recipients: list[str],
    template_context: dict | None = None,
) -> None:
    logger.info('Start channel set email code sending', extra={'log_meta': {'recipients': recipients}})
    try:
        await email_provider.send_channel_set_email_code(recipients=recipients, template_context=template_context)
    except AppException as e:
        logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
        raise
    logger.info('Complete channel set email code sending', extra={'log_meta': {'recipients': recipients}})


@broker.task(task_name='send_channel_reset_password_code_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_channel_reset_password_code_task(
    email_provider: FromDishka[IEmailProvider],
    recipients: list[str],
    template_context: dict | None = None,
) -> None:
    logger.info('Start channel reset password code sending', extra={'log_meta': {'recipients': recipients}})
    try:
        await email_provider.send_channel_reset_password_code(recipients=recipients, template_context=template_context)
    except AppException as e:
        logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
        raise
    logger.info('Complete channel reset password code sending', extra={'log_meta': {'recipients': recipients}})
