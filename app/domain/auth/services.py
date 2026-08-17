from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.parse import urlencode
from uuid import UUID, uuid4

from app.core.configs import settings
from app.domain.auth.exceptions import ChannelActivationInvalidCodeError
from app.domain.common.repositories.kv import IKVRepository


class IAuthService(ABC):
    @abstractmethod
    def build_activation_url(self, code: str, uid: str) -> str: ...

    @abstractmethod
    async def create_activation_code(self, channel_id: UUID) -> str: ...

    @abstractmethod
    async def validate_activation_code(self, channel_id: UUID, code: str) -> None: ...


@dataclass
class AuthService(IAuthService):
    _kv_repo: IKVRepository

    def _build_activation_key(self, channel_id: UUID) -> str:
        return f'auth:activation:code:{channel_id}'

    def build_activation_url(self, code: str, uid: str) -> str:
        activation_query = urlencode({'code': code, 'uid': uid})
        return f'{settings.frontend_origin}{settings.frontend_activation_uri}?{activation_query}'

    async def create_activation_code(self, channel_id: UUID) -> str:
        key = self._build_activation_key(channel_id=channel_id)
        code = uuid4().hex
        await self._kv_repo.set(key=key, value=code, ttl=60 * 5)
        return code

    async def validate_activation_code(self, channel_id: UUID, code: str) -> None:
        key = self._build_activation_key(channel_id=channel_id)
        saved_code = await self._kv_repo.get(key=key)

        if saved_code is None:
            raise ChannelActivationInvalidCodeError(
                channel_id=channel_id,
                code=code,
                reason='activation_code_not_found',
            )

        if saved_code != code:
            raise ChannelActivationInvalidCodeError(
                channel_id=channel_id,
                code=code,
                reason='activation_code_mismatch',
            )

        await self._kv_repo.delete(key=key)
