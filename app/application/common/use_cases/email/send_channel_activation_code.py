from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.email import SendChannelActivationCodeCommand
from app.application.common.interfaces.email_provider import IEmailProvider
from app.domain.common.exceptions import AppException

logger = getLogger(__name__)


@dataclass
class SendChannelActivationCodeUseCase:
    _email_provider: IEmailProvider

    async def execute(self, command: SendChannelActivationCodeCommand) -> None:
        template_context = {
            'name': command.name,
            'email': command.email,
            'activation_url': command.activation_url,
            'code': command.code,
        }

        logger.info('Start channel activation code sending', extra={'log_meta': {'recipient': command.email}})
        try:
            await self._email_provider.send_channel_activation_code(
                recipient=command.email, template_context=template_context
            )
        except AppException as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info('Complete channel activation code sending', extra={'log_meta': {'recipient': command.email}})
