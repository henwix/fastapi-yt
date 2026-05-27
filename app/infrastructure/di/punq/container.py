from functools import lru_cache

from punq import Container, Scope

from app.domain.common.interfaces.password_hasher import IPasswordHasher
from app.infrastructure.di.punq.channels import init_channels
from app.infrastructure.security.password_hashing import PwdlibPasswordHasher
from app.infrastructure.sqlalchemy.database import Database


@lru_cache(1)
def get_container() -> Container:
    return init_container()


def init_container() -> Container:
    container = Container()

    container.register(Database, scope=Scope.singleton)
    container.register(IPasswordHasher, PwdlibPasswordHasher)

    init_channels(container=container)

    return container
