from polyfactory.factories import DataclassFactory

from app.application.oauth.commands import OAuthDisconnectAccountCommand


class OAuthDisconnectAccountCommandFactory(DataclassFactory[OAuthDisconnectAccountCommand]):
    __model__ = OAuthDisconnectAccountCommand
