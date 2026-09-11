import secrets

from polyfactory.factories import DataclassFactory

from app.application.oauth.commands import OAuthDisconnectAccountCommand, OAuthVerifyCodeCommand


class OAuthDisconnectAccountCommandFactory(DataclassFactory[OAuthDisconnectAccountCommand]):
    __model__ = OAuthDisconnectAccountCommand


class OAuthVerifyCodeCommandFactory(DataclassFactory[OAuthVerifyCodeCommand]):
    __model__ = OAuthVerifyCodeCommand

    @classmethod
    def code(cls) -> str:
        return secrets.token_hex(16)

    @classmethod
    def state(cls) -> str:
        return secrets.token_hex(16)
