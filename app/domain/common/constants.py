from enum import Enum


class Empty(Enum):
    UNSET = 'UNSET'


SLUG_PATTERN = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'

FILENAME_PATTERN = r'^[A-Za-z0-9_-]+\.[A-Za-z0-9]+$'
