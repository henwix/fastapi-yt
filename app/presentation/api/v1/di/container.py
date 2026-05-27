from typing import Annotated

from fastapi import Depends
from punq import Container

from app.infrastructure.di.punq.container import get_container

PunqContainer = Annotated[Container, Depends(get_container)]
