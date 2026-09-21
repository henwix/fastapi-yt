from dishka import Provider

from .app import AppProvider
from .database import DatabaseProvider
from .oauth import OAuthProvider
from .readers import ReadersProvider
from .repos import ReposProvider
from .services import ServicesProvider
from .usecases import UseCasesProvider


def get_providers() -> list[Provider]:
    return [
        AppProvider(),
        DatabaseProvider(),
        OAuthProvider(),
        ReadersProvider(),
        ReposProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    ]


__all__ = (
    'AppProvider',
    'DatabaseProvider',
    'OAuthProvider',
    'ReadersProvider',
    'ReposProvider',
    'ServicesProvider',
    'UseCasesProvider',
    'get_providers',
)
