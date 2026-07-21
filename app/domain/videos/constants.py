VIDEO_ID_PATTERN = r'^[A-Za-z0-9_-]{11}$'

VIDEO_TITLE_MIN_LENGTH = 1
VIDEO_TITLE_MAX_LENGTH = 100

VIDEO_DESCRIPTION_MAX_LENGTH = 5000

VIDEO_FILE_MIME_TYPES = {
    '.mp4': 'video/mp4',
    '.mov': 'video/quicktime',
    '.mkv': 'video/matroska',
    '.webm': 'video/webm',
}
