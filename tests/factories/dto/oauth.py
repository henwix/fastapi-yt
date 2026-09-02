from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.oauth.dto import OAuthProviderUserData


class OAuthProviderUserDataFactory(DataclassFactory[OAuthProviderUserData]):
    __faker__ = Faker()
    __model__ = OAuthProviderUserData

    @classmethod
    def uid(cls) -> str:
        return cls.__faker__.numerify('#' * 30)

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()

    @classmethod
    def login(cls) -> str:
        return cls.__faker__.user_name()

    @classmethod
    def name(cls) -> str:
        return cls.__faker__.name()
