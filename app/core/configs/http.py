from pydantic import Field
from pydantic_settings import BaseSettings


class HttpSettings(BaseSettings):
    http_default_timeout: int = Field(default=5)
    http_max_connections: int = Field(default=100)
    http_max_keepalive_connections: int = Field(default=20)
    http_keepalive_expiry: int = Field(default=5)
