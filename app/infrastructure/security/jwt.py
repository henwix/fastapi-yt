import secrets
from datetime import timedelta

import jwt

from app.application.common.dto.jwt import JWTAccessToken, JWTRefreshToken, JWTTokenPayload
from app.application.common.interfaces.jwt import IJWTService
from app.core.configs import settings
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError
from app.utils.datetime import get_current_utc_datetime


class JWTService(IJWTService):
    _ALGORITHM: str = settings.jwt_algorithm
    _ACCESS_SECRET: str = settings.jwt_access_secret_key
    _REFRESH_SECRET: str = settings.jwt_refresh_secret_key
    _ACCESS_EXP_MINUTES: int = settings.jwt_access_exp_minutes
    _REFRESH_EXP_DAYS: int = settings.jwt_refresh_exp_days
    _ACCESS_TOKEN_TYPE: str = 'access'
    _REFRESH_TOKEN_TYPE: str = 'refresh'
    _ACCESS_REQUIRED_CLAIMS: list[str] = ['sub', 'token_type', 'exp']
    _REFRESH_REQUIRED_CLAIMS: list[str] = ['sub', 'token_type', 'exp', 'jti']

    def _create_jti(self) -> str:
        return secrets.token_hex(8)

    def _create_token(self, sub: str, key: str, token_type: str, exp: timedelta, jti: str | None = None) -> str:
        payload = {
            'sub': sub,
            'token_type': token_type,
            'exp': get_current_utc_datetime() + exp,
        }
        if jti is not None:
            payload['jti'] = jti

        return jwt.encode(payload=payload, key=key, algorithm=self._ALGORITHM)

    def _decode_token(self, token: str, key: str, token_type: str, required_claims: list[str]) -> JWTTokenPayload:
        try:
            payload = jwt.decode(
                jwt=token,
                key=key,
                algorithms=[self._ALGORITHM],
                options={'require': required_claims},
            )
            payload_jti = payload.get('jti')
            payload_sub = payload['sub']
            payload_token_type = payload['token_type']

            if payload_token_type != token_type:
                raise JWTInvalidTokenError(error_detail='invalid_token_type')

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

        return JWTTokenPayload(token_type=payload_token_type, sub=payload_sub, jti=payload_jti)

    def create_access_token(self, sub: str) -> JWTAccessToken:
        access_token = self._create_token(
            sub=sub,
            key=self._ACCESS_SECRET,
            token_type=self._ACCESS_TOKEN_TYPE,
            exp=timedelta(minutes=self._ACCESS_EXP_MINUTES),
        )
        return JWTAccessToken(token=access_token)

    def create_refresh_token(self, sub: str) -> JWTRefreshToken:
        jti = self._create_jti()
        refresh_token = self._create_token(
            sub=sub,
            key=self._REFRESH_SECRET,
            token_type=self._REFRESH_TOKEN_TYPE,
            exp=timedelta(days=self._REFRESH_EXP_DAYS),
            jti=jti,
        )
        return JWTRefreshToken(token=refresh_token, jti=jti)

    def decode_access_token(self, token: str) -> JWTTokenPayload:
        return self._decode_token(
            token=token,
            key=self._ACCESS_SECRET,
            token_type=self._ACCESS_TOKEN_TYPE,
            required_claims=self._ACCESS_REQUIRED_CLAIMS,
        )

    def decode_refresh_token(self, token: str) -> JWTTokenPayload:
        return self._decode_token(
            token=token,
            key=self._REFRESH_SECRET,
            token_type=self._REFRESH_TOKEN_TYPE,
            required_claims=self._REFRESH_REQUIRED_CLAIMS,
        )

    def decode_unverified_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(jwt=token, options={'verify_signature': False})
            return payload
        except jwt.InvalidTokenError as e:
            raise JWTInvalidTokenError(error_detail='invalid_token') from e
