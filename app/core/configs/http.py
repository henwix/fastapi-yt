from pydantic import Field
from pydantic_settings import BaseSettings


class HttpSettings(BaseSettings):
    http_default_timeout: int = Field(default=5, alias='HTTP_DEFAULT_TIMEOUT')
    http_max_connections: int = Field(default=100, alias='HTTP_MAX_CONNECTIONS')
    http_max_keepalive_connections: int = Field(default=20, alias='HTTP_MAX_KEEPALIVE_CONNECTIONS')
    http_keepalive_expiry: int = Field(default=5, alias='HTTP_KEEPALIVE_EXPIRY')
