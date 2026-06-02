from dataclasses import dataclass

from app.domain.common.constants import Empty


@dataclass
class CreateChannelCommand:
    email: str
    name: str
    slug: str
    description: str
    country: str
    password: str


@dataclass
class UpdateChannelCommand:
    channel_id: int
    name: str | Empty = Empty.UNSET
    slug: str | Empty = Empty.UNSET
    description: str | Empty = Empty.UNSET
    country: str | Empty = Empty.UNSET


@dataclass
class DeleteChannelCommand:
    channel_id: int
