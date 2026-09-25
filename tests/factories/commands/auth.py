import secrets
from uuid import uuid7

from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.auth.commands import (
    ActivateChannelCommand,
    LoginWithEmailCodeCommand,
    LoginWithEmailCodeConfirmCommand,
    LoginWithPasswordCommand,
    RegisterChannelWithEmailCommand,
    RegisterChannelWithPasswordCommand,
    ResendChannelActivationCodeCommand,
    ResetChannelPasswordCommand,
    ResetChannelPasswordConfirmCommand,
    SetChannelEmailCommand,
    SetChannelEmailConfirmCommand,
    SetChannelPasswordCommand,
)
from app.utils.base64url import base64url_encode


class RegisterChannelWithPasswordCommandFactory(DataclassFactory[RegisterChannelWithPasswordCommand]):
    __model__ = RegisterChannelWithPasswordCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()

    @classmethod
    def slug(cls) -> str:
        return cls.__faker__.slug()


class RegisterChannelWithEmailCommandFactory(DataclassFactory[RegisterChannelWithEmailCommand]):
    __model__ = RegisterChannelWithEmailCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()

    @classmethod
    def slug(cls) -> str:
        return cls.__faker__.slug()


class LoginWithPasswordCommandFactory(DataclassFactory[LoginWithPasswordCommand]):
    __model__ = LoginWithPasswordCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()


class LoginWithEmailCodeCommandFactory(DataclassFactory[LoginWithEmailCodeCommand]):
    __model__ = LoginWithEmailCodeCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()


class LoginWithEmailCodeConfirmCommandFactory(DataclassFactory[LoginWithEmailCodeConfirmCommand]):
    __faker__ = Faker()
    __model__ = LoginWithEmailCodeConfirmCommand

    @classmethod
    def code(cls) -> str:
        return secrets.token_hex(16)

    @classmethod
    def uid(cls) -> str:
        return base64url_encode(value=str(uuid7()))


class SetChannelPasswordCommandFactory(DataclassFactory[SetChannelPasswordCommand]):
    __model__ = SetChannelPasswordCommand


class ActivateChannelCommandFactory(DataclassFactory[ActivateChannelCommand]):
    __model__ = ActivateChannelCommand

    @classmethod
    def code(cls) -> str:
        return secrets.token_hex(16)


class ResendChannelActivationCodeCommandFactory(DataclassFactory[ResendChannelActivationCodeCommand]):
    __model__ = ResendChannelActivationCodeCommand


class SetChannelEmailCommandFactory(DataclassFactory[SetChannelEmailCommand]):
    __faker__ = Faker()
    __model__ = SetChannelEmailCommand

    @classmethod
    def new_email(cls) -> str:
        return cls.__faker__.email()


class SetChannelEmailConfirmCommandFactory(DataclassFactory[SetChannelEmailConfirmCommand]):
    __model__ = SetChannelEmailConfirmCommand

    @classmethod
    def code(cls) -> str:
        return secrets.token_hex(16)


class ResetChannelPasswordCommandFactory(DataclassFactory[ResetChannelPasswordCommand]):
    __faker__ = Faker()
    __model = ResetChannelPasswordCommand

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()


class ResetChannelPasswordConfirmCommandFactory(DataclassFactory[ResetChannelPasswordConfirmCommand]):
    __faker__ = Faker()
    __model__ = ResetChannelPasswordConfirmCommand

    @classmethod
    def code(cls) -> str:
        return secrets.token_hex(16)

    @classmethod
    def uid(cls) -> str:
        return base64url_encode(value=str(uuid7()))

    @classmethod
    def new_password(cls) -> str:
        return cls.__faker__.password()
