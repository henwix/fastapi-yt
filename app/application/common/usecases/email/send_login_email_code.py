from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.email import SendLoginEmailCodeCommand
from app.application.common.interfaces.email import IEmailProvider
from app.domain.common.exceptions.base import AppError

logger = getLogger(__name__)


@dataclass
class SendLoginEmailCodeUseCase:
    _email_provider: IEmailProvider

    async def execute(self, command: SendLoginEmailCodeCommand) -> None:
        template_context = {
            'email': command.email,
            'name': command.name,
            'confirmation_url': command.confirmation_url,
            'code': command.code,
            'uid': command.uid,
        }
        logger.info('Start login email code sending', extra={'log_meta': {'recipient': command.email}})
        try:
            await self._email_provider.send_login_email_code(recipient=command.email, template_context=template_context)
        except AppError as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info('Complete login email code sending', extra={'log_meta': {'recipient': command.email}})
