import secrets
import string

POSSIBLE_VIDEO_ID_CHARS = f'{string.digits}{string.ascii_letters}-_'


def generate_video_id() -> str:
    return ''.join(secrets.choice(POSSIBLE_VIDEO_ID_CHARS) for _ in range(11))
