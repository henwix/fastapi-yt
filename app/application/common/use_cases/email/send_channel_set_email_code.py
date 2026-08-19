from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.email import SendChannelSetEmailCodeCommand
from app.application.common.interfaces.email_provider import IEmailProvider
from app.domain.common.exceptions import AppException

logger = getLogger(__name__)


@dataclass
class SendChannelSetEmailCodeUseCase:
    _email_provider: IEmailProvider

    async def execute(self, command: SendChannelSetEmailCodeCommand) -> None:
        template_context = {
            'email': command.email,
            'name': command.name,
            'confirmation_url': command.confirmation_url,
            'code': command.code,
        }

        logger.info('Start channel set email code sending', extra={'log_meta': {'recipient': command.email}})
        try:
            await self._email_provider.send_channel_set_email_code(
                recipient=command.email, template_context=template_context
            )
        except AppException as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info('Complete channel set email code sending', extra={'log_meta': {'recipient': command.email}})
