from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.channels.exceptions import ChannelWithEmailAlreadyExists, ChannelWithSlugAlreadyExists
from app.domain.channels.repository import IChannelRepository


class IChannelValidatorService(ABC):
    @abstractmethod
    async def validate(self, email: str, slug: str) -> None: ...


@dataclass
class ChannelUniqueEmailValidatorService(IChannelValidatorService):
    channels_repository: IChannelRepository

    async def validate(self, email: str, *args, **kwargs) -> None:
        if await self.channels_repository.check_channel_exists_by_email(email=email):
            raise ChannelWithEmailAlreadyExists(email=email)


@dataclass
class ChannelUniqueSlugValidatorService(IChannelValidatorService):
    channels_repository: IChannelRepository

    async def validate(self, slug: str, *args, **kwargs) -> None:
        if await self.channels_repository.check_channel_exists_by_slug(slug=slug):
            raise ChannelWithSlugAlreadyExists(slug=slug)


@dataclass
class ComposedChannelValidatorService(IChannelValidatorService):
    validators: list[IChannelValidatorService]

    async def validate(self, email: str, slug: str) -> None:
        for validator in self.validators:
            await validator.validate(email=email, slug=slug)
