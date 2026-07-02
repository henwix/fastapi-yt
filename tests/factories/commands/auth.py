from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.auth.commands import LoginCommand


class LoginCommandFactory(DataclassFactory[LoginCommand]):
    __model__ = LoginCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()
