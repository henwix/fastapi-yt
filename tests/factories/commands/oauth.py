from uuid import uuid4

from polyfactory.factories import DataclassFactory

from app.application.oauth.commands import OAuthDisconnectAccountCommand, OAuthVerifyCodeCommand


class OAuthDisconnectAccountCommandFactory(DataclassFactory[OAuthDisconnectAccountCommand]):
    __model__ = OAuthDisconnectAccountCommand


class OAuthVerifyCodeCommandFactory(DataclassFactory[OAuthVerifyCodeCommand]):
    __model__ = OAuthVerifyCodeCommand

    @classmethod
    def code(cls) -> str:
        return uuid4().hex

    @classmethod
    def state(cls) -> str:
        return uuid4().hex
