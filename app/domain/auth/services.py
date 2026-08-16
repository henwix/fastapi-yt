from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID, uuid4

from app.domain.auth.exceptions import ChannelActivationInvalidCodeError
from app.domain.common.repositories.kv import IKVRepository


class IAuthService(ABC):
    @abstractmethod
    async def create_activation_code(self, channel_id: UUID) -> str: ...

    @abstractmethod
    async def validate_activation_code(self, channel_id: UUID, code: str) -> None: ...


@dataclass
class AuthService(IAuthService):
    _kv_repo: IKVRepository

    def _build_activation_key(self, channel_id: UUID) -> str:
        return f'auth:activation:code:{channel_id}'

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
