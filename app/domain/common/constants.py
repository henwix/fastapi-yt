from enum import Enum


class Empty(Enum):
    UNSET = 'UNSET'


SLUG_PATTERN = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'

EMAIL_PATTERN = r'[a-z0-9._%+-]+@(?:[a-z0-9-]+\.)+[a-z]{2,}'

FILENAME_PATTERN = r'^[A-Za-z0-9_-]+\.[A-Za-z0-9]+$'
FILENAME_MAX_LENGTH = 100

IMAGE_FILE_MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
}

VIDEO_FILE_MIME_TYPES = {
    '.mp4': ['video/mp4'],
    '.mov': ['video/quicktime'],
    '.mkv': ['video/matroska', 'video/x-matroska'],
    '.webm': ['video/webm'],
}
