from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto.base import DTO
from app.domain.channels.enums import ChannelDeletionStatusEnum


@dataclass(kw_only=True)
class ChannelAboutInfo(DTO):
    id: UUID
    name: str
    slug: str
    description: str
    country: str
    created_at: datetime
    subscribers_count: int
    videos_count: int
    views_count: int


@dataclass(kw_only=True)
class DetailedChannel(DTO):
    id: UUID
    name: str
    email: str
    slug: str
    description: str
    country: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deletion_status: ChannelDeletionStatusEnum
    deleted_at: datetime | None
    avatar_url: str | None


@dataclass(kw_only=True)
class PurgeDeletedChannelsResult(DTO):
    total_files_deleted: int
    total_cleanups_created: int
    total_channels_deleted: int
