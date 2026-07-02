from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.subscriptions.commands import SubscribeCommand, UnsubscribeCommand


class SubscribeCommandFactory(DataclassFactory[SubscribeCommand]):
    __model__ = SubscribeCommand
    __faker__ = Faker()

    @classmethod
    def channel_slug(cls) -> str:
        return cls.__faker__.slug()


class UnsubscribeCommandFactory(DataclassFactory[UnsubscribeCommand]):
    __model__ = UnsubscribeCommand
    __faker__ = Faker()

    @classmethod
    def channel_slug(cls) -> str:
        return cls.__faker__.slug()
