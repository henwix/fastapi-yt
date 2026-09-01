from uuid import uuid4

from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.auth.commands import (
    ActivateChannelCommand,
    LoginChannelCommand,
    RegisterChannelCommand,
    ResendChannelActivationCodeCommand,
    SetChannelEmailCommand,
    SetChannelEmailConfirmCommand,
    SetChannelPasswordCommand,
)


class RegisterChannelCommandFactory(DataclassFactory[RegisterChannelCommand]):
    __model__ = RegisterChannelCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()

    @classmethod
    def slug(cls) -> str:
        return cls.__faker__.slug()


class LoginChannelCommandFactory(DataclassFactory[LoginChannelCommand]):
    __model__ = LoginChannelCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()


class SetChannelPasswordCommandFactory(DataclassFactory[SetChannelPasswordCommand]):
    __model__ = SetChannelPasswordCommand


class ActivateChannelCommandFactory(DataclassFactory[ActivateChannelCommand]):
    __model__ = ActivateChannelCommand

    @classmethod
    def code(cls) -> str:
        return uuid4().hex


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
        return uuid4().hex
