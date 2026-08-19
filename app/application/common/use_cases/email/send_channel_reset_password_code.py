from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.email import SendChannelResetPasswordCodeCommand
from app.application.common.interfaces.email_provider import IEmailProvider
from app.domain.common.exceptions import AppException

logger = getLogger(__name__)


@dataclass
class SendChannelResetPasswordCodeUseCase:
    _email_provider: IEmailProvider

    async def execute(self, command: SendChannelResetPasswordCodeCommand) -> None:
        template_context = {
            'email': command.email,
            'name': command.name,
            'confirmation_url': command.confirmation_url,
            'code': command.code,
            'uid': command.uid,
        }
        logger.info('Start channel reset password code sending', extra={'log_meta': {'recipient': command.email}})
        try:
            await self._email_provider.send_channel_reset_password_code(
                recipient=command.email, template_context=template_context
            )
        except AppException as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info('Complete channel reset password code sending', extra={'log_meta': {'recipient': command.email}})
