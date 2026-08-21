from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.commands.email import (
    SendChannelActivationCodeCommand,
    SendChannelResetPasswordCodeCommand,
    SendChannelSetEmailCodeCommand,
)
from app.application.common.use_cases.email.send_channel_activation_code import SendChannelActivationCodeUseCase
from app.application.common.use_cases.email.send_channel_reset_password_code import SendChannelResetPasswordCodeUseCase
from app.application.common.use_cases.email.send_channel_set_email_code import SendChannelSetEmailCodeUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='send_channel_activation_code_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_channel_activation_code_task(
    command: SendChannelActivationCodeCommand,
    use_case: FromDishka[SendChannelActivationCodeUseCase],
) -> None:
    await use_case.execute(command=command)


@broker.task(task_name='send_channel_set_email_code_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_channel_set_email_code_task(
    command: SendChannelSetEmailCodeCommand,
    use_case: FromDishka[SendChannelSetEmailCodeUseCase],
) -> None:
    await use_case.execute(command=command)


@broker.task(task_name='send_channel_reset_password_code_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def send_channel_reset_password_code_task(
    command: SendChannelResetPasswordCodeCommand,
    use_case: FromDishka[SendChannelResetPasswordCodeUseCase],
) -> None:
    await use_case.execute(command=command)
