from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.auth.commands import LoginChannelCommand, RegisterChannelCommand, SetChannelPasswordCommand


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
