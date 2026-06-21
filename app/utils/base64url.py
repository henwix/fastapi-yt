from base64 import urlsafe_b64decode, urlsafe_b64encode

import msgspec


def base64url_encode(value: dict) -> str:
    bt = msgspec.json.encode(value)
    return urlsafe_b64encode(bt).rstrip(b'=').decode()


def base64url_decode(value: str) -> dict:
    padding = '=' * (-len(value) % 4)
    bt = urlsafe_b64decode(value + padding)
    return msgspec.json.decode(bt)
