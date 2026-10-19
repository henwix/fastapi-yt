from enum import StrEnum


class ChannelDeletionStatusEnum(StrEnum):
    ACTIVE = 'active'
    DELETED = 'deleted'
    PURGING = 'purging'
