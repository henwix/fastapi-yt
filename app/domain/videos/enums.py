from enum import StrEnum


class VideoPrivacyStatusEnum(StrEnum):
    PUBLIC = 'public'
    UNLISTED = 'unlisted'
    PRIVATE = 'private'


class VideoUploadStatusEnum(StrEnum):
    UPLOADING = 'uploading'
    COMPLETED = 'completed'


class VideoFileContentTypesEnum(StrEnum):
    MP4 = 'video/mp4'
    MOV = 'video/quicktime'
    MKV = 'video/matroska'
    WEBM = 'video/webm'
