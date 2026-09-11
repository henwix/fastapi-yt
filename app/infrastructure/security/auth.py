from dataclasses import dataclass
from uuid import UUID

from app.application.common.dto.jwt import JWTRefreshToken, JWTTokens
from app.application.common.interfaces.auth import IAuthService
from app.application.common.interfaces.jwt import IJWTService
from app.core.configs import settings
from app.domain.auth.exceptions import JWTTokenNotFoundError
from app.domain.common.repos.kv import IKVRepo


@dataclass
class AuthService(IAuthService):
    _kv_repo: IKVRepo
    _jwt_service: IJWTService

    def _build_refresh_token_key(self, channel_id: str, jti: str) -> str:
        return f'auth:refresh_token:{channel_id}:{jti}'

    async def _save_refresh_token(self, channel_id: str, jti: str) -> None:
        refresh_token_key = self._build_refresh_token_key(channel_id=channel_id, jti=jti)
        await self._kv_repo.set(
            key=refresh_token_key,
            value='',
            ttl_seconds=settings.jwt_refresh_exp_days * 24 * 60 * 60,
        )

    async def login(self, channel_id: UUID) -> JWTTokens:
        channel_id_str = str(channel_id)
        access_token = self._jwt_service.create_access_token(sub=channel_id_str)
        refresh_token = self._jwt_service.create_refresh_token(sub=channel_id_str)
        await self._save_refresh_token(channel_id=channel_id_str, jti=refresh_token.jti)
        return JWTTokens(access=access_token, refresh=refresh_token)

    async def logout(self, refresh: str) -> None:
        token_payload = self._jwt_service.decode_refresh_token(token=refresh)
        refresh_token_key = self._build_refresh_token_key(
            channel_id=token_payload.sub,
            jti=token_payload.jti,
        )
        if not await self._kv_repo.delete(key=refresh_token_key):
            raise JWTTokenNotFoundError

    async def refresh(self, refresh: str) -> JWTTokens:
        token_payload = self._jwt_service.decode_refresh_token(token=refresh)
        channel_id = token_payload.sub

        refresh_token_key = self._build_refresh_token_key(
            channel_id=channel_id,
            jti=token_payload.jti,
        )
        if await self._kv_repo.get(key=refresh_token_key) is None:
            raise JWTTokenNotFoundError

        access_token = self._jwt_service.create_access_token(sub=channel_id)

        if settings.jwt_rotate_refresh_token:
            await self._kv_repo.delete(key=refresh_token_key)
            new_refresh_token = self._jwt_service.create_refresh_token(sub=channel_id)
            await self._save_refresh_token(channel_id=channel_id, jti=new_refresh_token.jti)
            return JWTTokens(access=access_token, refresh=new_refresh_token)

        return JWTTokens(access=access_token, refresh=JWTRefreshToken(token=refresh, jti=token_payload.jti))
