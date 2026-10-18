from enum import StrEnum


class FileCleanupStatusEnum(StrEnum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    FAILED = 'failed'
