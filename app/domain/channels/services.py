from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
    ChannelWithEmailAlreadyExistsError,
    ChannelWithSlugAlreadyExistsError,
)
from app.domain.channels.repositories import IChannelRepository


class IChannelService(ABC):
    @abstractmethod
    async def check_email_exists(self, email: str) -> None: ...

    @abstractmethod
    async def check_slug_exists(self, slug: str) -> None: ...

    @abstractmethod
    async def create(self, channel: Channel) -> Channel: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Channel | None: ...

    @abstractmethod
    async def try_get_by_slug(self, slug: str) -> Channel: ...

    @abstractmethod
    async def try_get_active_by_id(self, id: UUID) -> Channel: ...

    @abstractmethod
    async def try_update(self, channel: Channel) -> Channel: ...

    @abstractmethod
    async def try_set_password(self, id: UUID, password_hash: str) -> None: ...

    @abstractmethod
    async def try_delete_by_id(self, id: UUID) -> None: ...


@dataclass
class ChannelService(IChannelService):
    _channel_repo: IChannelRepository

    async def check_email_exists(self, email: str) -> None:
        if await self._channel_repo.check_channel_exists_by_email(email=email):
            raise ChannelWithEmailAlreadyExistsError(email=email)

    async def check_slug_exists(self, slug: str) -> None:
        if await self._channel_repo.check_channel_exists_by_slug(slug=slug):
            raise ChannelWithSlugAlreadyExistsError(slug=slug)

    async def create(self, channel: Channel) -> Channel:
        return await self._channel_repo.create(channel=channel)

    async def get_by_email(self, email: str) -> Channel | None:
        return await self._channel_repo.get_by_email(email=email)

    async def try_get_by_slug(self, slug: str) -> Channel:
        channel = await self._channel_repo.get_by_slug(slug=slug)
        if not channel:
            raise ChannelNotFoundBySlugError(slug=slug)
        return channel

    async def try_get_active_by_id(self, id: UUID) -> Channel:
        channel = await self._channel_repo.get_by_id(id=id)
        if not channel:
            raise ChannelNotFoundByIdError(id=id)
        if not channel.is_active:
            raise ChannelNotActiveError(id=channel.id)
        return channel

    async def try_update(self, channel: Channel) -> Channel:
        updated_channel = await self._channel_repo.update(channel=channel)
        if not updated_channel:
            raise ChannelNotFoundByIdError(id=channel.id)
        return updated_channel

    async def try_set_password(self, id: UUID, password_hash: str) -> None:
        is_password_set = await self._channel_repo.set_password(id=id, password_hash=password_hash)
        if not is_password_set:
            raise ChannelNotFoundByIdError(id=id)

    async def try_delete_by_id(self, id: UUID) -> None:
        is_deleted = await self._channel_repo.delete_by_id(id=id)
        if not is_deleted:
            raise ChannelNotFoundByIdError(id=id)
