from punq import Container

from app.application.use_cases.channels.create_channel import CreateChannelUseCase
from app.domain.channels.repository import IChannelRepository
from app.infrastructure.sqlalchemy.repositories.channels import SAChannelRepository


def init_channels(container: Container) -> None:
    # use cases
    container.register(CreateChannelUseCase)

    # repositories
    container.register(IChannelRepository, SAChannelRepository)
