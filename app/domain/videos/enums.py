from enum import StrEnum


class VideoPrivacyStatusEnum(StrEnum):
    PUBLIC = 'public'
    UNLISTED = 'unlisted'
    PRIVATE = 'private'


class VideoUploadStatusEnum(StrEnum):
    PENDING = 'pending'
    UPLOADING = 'uploading'
    COMPLETED = 'completed'


class VideoDeletionStatusEnum(StrEnum):
    ACTIVE = 'active'
    DELETED = 'deleted'
    PURGING = 'purging'
