from pydantic_settings import BaseSettings


class HttpSettings(BaseSettings):
    http_default_timeout: int = 5
    http_max_connections: int = 100
    http_max_keepalive_connections: int = 20
    http_keepalive_expiry: int = 5
