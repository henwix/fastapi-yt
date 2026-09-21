import secrets

from polyfactory.factories import DataclassFactory

from app.application.oauth.commands import DisconnectOAuthAccountCommand, VerifyOAuthCodeCommand


class DisconnectOAuthAccountCommandFactory(DataclassFactory[DisconnectOAuthAccountCommand]):
    __model__ = DisconnectOAuthAccountCommand


class VerifyOAuthCodeCommandFactory(DataclassFactory[VerifyOAuthCodeCommand]):
    __model__ = VerifyOAuthCodeCommand

    @classmethod
    def code(cls) -> str:
        return secrets.token_hex(16)

    @classmethod
    def state(cls) -> str:
        return secrets.token_hex(16)
