from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.parse import urlencode
from uuid import UUID, uuid4

import msgspec

from app.core.configs import settings
from app.domain.auth.exceptions import (
    ChannelActivationInvalidCodeError,
    ChannelResetPasswordInvalidCodeError,
    ChannelSetEmailInvalidCodeError,
)
from app.domain.common.repositories.kv import IKVRepository


class IAuthService(ABC):
    @abstractmethod
    def build_activation_url(self, code: str, uid: str) -> str: ...

    @abstractmethod
    async def create_activation_code(self, channel_id: UUID) -> str: ...

    @abstractmethod
    async def validate_activation_code(self, channel_id: UUID, code: str) -> None: ...

    @abstractmethod
    def build_set_email_confirm_url(self, code: str) -> str: ...

    @abstractmethod
    async def create_set_email_code(self, channel_id: UUID, new_email: str) -> str: ...

    @abstractmethod
    async def validate_set_email_code(self, channel_id: UUID, code: str) -> str: ...

    @abstractmethod
    def build_reset_password_confirm_url(self, code: str, uid: str) -> str: ...

    @abstractmethod
    async def create_reset_password_code(self, channel_id: UUID) -> str: ...

    @abstractmethod
    async def validate_reset_password_code(self, channel_id: UUID, code: str) -> str: ...


@dataclass
class AuthService(IAuthService):
    _kv_repo: IKVRepository

    def _build_activation_key(self, channel_id: UUID) -> str:
        return f'auth:activation:code:{channel_id}'

    def _build_set_email_key(self, channel_id: UUID) -> str:
        return f'auth:set_email:code:{channel_id}'

    def _build_reset_password_key(self, channel_id: UUID) -> str:
        return f'auth:reset_password:code:{channel_id}'

    def build_activation_url(self, code: str, uid: str) -> str:
        query = urlencode({'code': code, 'uid': uid})
        return f'{settings.frontend_origin}{settings.frontend_activation_uri}?{query}'

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

    def build_set_email_confirm_url(self, code: str) -> str:
        query = urlencode({'code': code})
        return f'{settings.frontend_origin}{settings.frontend_set_email_confirm_uri}?{query}'

    async def create_set_email_code(self, channel_id: UUID, new_email: str) -> str:
        key = self._build_set_email_key(channel_id=channel_id)
        code = uuid4().hex
        value = msgspec.json.encode({'code': code, 'new_email': new_email})
        await self._kv_repo.set(key=key, value=value, ttl=60 * 5)
        return code

    async def validate_set_email_code(self, channel_id: UUID, code: str) -> str:
        key = self._build_set_email_key(channel_id=channel_id)
        saved_code_and_new_email = await self._kv_repo.get(key=key)

        if saved_code_and_new_email is None:
            raise ChannelSetEmailInvalidCodeError(
                channel_id=channel_id,
                code=code,
                reason='set_email_code_not_found',
            )

        decoded_code_and_new_email: dict[str, str] = msgspec.json.decode(saved_code_and_new_email)

        if decoded_code_and_new_email['code'] != code:
            raise ChannelSetEmailInvalidCodeError(
                channel_id=channel_id,
                code=code,
                reason='set_email_code_mismatch',
            )

        await self._kv_repo.delete(key=key)
        return decoded_code_and_new_email['new_email']

    def build_reset_password_confirm_url(self, code: str, uid: str) -> str:
        query = urlencode({'code': code, 'uid': uid})
        return f'{settings.frontend_origin}{settings.frontend_reset_password_confirm_uri}?{query}'

    async def create_reset_password_code(self, channel_id: UUID) -> str:
        key = self._build_reset_password_key(channel_id=channel_id)
        code = uuid4().hex
        await self._kv_repo.set(key=key, value=code, ttl=60 * 5)
        return code

    async def validate_reset_password_code(self, channel_id: UUID, code: str) -> None:
        key = self._build_reset_password_key(channel_id=channel_id)
        saved_code = await self._kv_repo.get(key=key)

        if saved_code is None:
            raise ChannelResetPasswordInvalidCodeError(
                channel_id=channel_id,
                code=code,
                reason='reset_password_code_not_found',
            )

        if saved_code != code:
            raise ChannelResetPasswordInvalidCodeError(
                channel_id=channel_id,
                code=code,
                reason='reset_password_code_mismatch',
            )

        await self._kv_repo.delete(key=key)
