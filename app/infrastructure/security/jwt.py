from datetime import timedelta
from typing import Any
from uuid import UUID

import jwt

from app.application.common.jwt import IJWTService
from app.core.configs import settings
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError
from app.utils.get_datetime_utc_now import get_datetime_utc_now


class JWTService(IJWTService):
    _ACCESS_SECRET: str = settings.jwt_access_secret_key
    _REFRESH_SECRET: str = settings.jwt_refresh_secret_key
    _ALGORITHM: str = settings.jwt_algorithm
    _ACCESS_EXP_DAYS: int = settings.jwt_access_exp_days
    _REFRESH_EXP_DAYS: int = settings.jwt_refresh_exp_days
    _ACCESS_TOKEN_TYPE: str = 'access'
    _REFRESH_TOKEN_TYPE: str = 'refresh'
    _REQUIRED_CLAIMS: list[str] = ['sub', 'token_type', 'exp']

    def _create_token(self, sub: str, key: str, token_type: str, exp_days: int) -> str:
        payload = {
            'sub': sub,
            'token_type': token_type,
            'exp': get_datetime_utc_now() + timedelta(days=exp_days),
        }
        return jwt.encode(payload=payload, key=key, algorithm=self._ALGORITHM)

    def _validate_payload(self, payload: dict[str, Any], token_type: str) -> None:
        if payload['token_type'] != token_type:
            raise JWTInvalidTokenError(error_detail='invalid_token_type')

    def _decode_token(self, token: str, key: str, token_type: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(
                jwt=token,
                key=key,
                algorithms=[self._ALGORITHM],
                options={'require': self._REQUIRED_CLAIMS},
            )
            self._validate_payload(payload=payload, token_type=token_type)

        except jwt.ExpiredSignatureError as e:
            raise JWTExpiredTokenError from e

        except jwt.InvalidSignatureError as e:
            raise JWTInvalidTokenError(error_detail='invalid_signature') from e

        except jwt.MissingRequiredClaimError as e:
            raise JWTInvalidTokenError(error_detail='missing_required_claim') from e

        except jwt.InvalidAlgorithmError:
            raise

        except jwt.InvalidTokenError as e:
            raise JWTInvalidTokenError(error_detail='invalid_token') from e

        try:
            payload['sub'] = UUID(payload['sub'])
            return payload
        except (ValueError, TypeError) as e:
            raise JWTInvalidTokenError(error_detail='invalid_sub_type') from e

    def create_access_token(self, sub: str) -> str:
        return self._create_token(
            sub=sub,
            key=self._ACCESS_SECRET,
            token_type=self._ACCESS_TOKEN_TYPE,
            exp_days=self._ACCESS_EXP_DAYS,
        )

    def create_refresh_token(self, sub: str) -> str:
        return self._create_token(
            sub=sub,
            key=self._REFRESH_SECRET,
            token_type=self._REFRESH_TOKEN_TYPE,
            exp_days=self._REFRESH_EXP_DAYS,
        )

    def create_tokens(self, sub: UUID) -> dict[str, str]:
        return {
            'access': self.create_access_token(sub=str(sub)),
            'refresh': self.create_refresh_token(sub=str(sub)),
        }

    def decode_access_token(self, token: str) -> dict[str, Any]:
        return self._decode_token(token=token, key=self._ACCESS_SECRET, token_type=self._ACCESS_TOKEN_TYPE)

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        return self._decode_token(token=token, key=self._REFRESH_SECRET, token_type=self._REFRESH_TOKEN_TYPE)
