from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_user: str = Field(alias='POSTGRES_USER')
    db_password: str = Field(alias='POSTGRES_PASSWORD')
    db_name: str = Field(alias='POSTGRES_DB')
    db_host: str = Field(alias='POSTGRES_HOST')
    db_port: int = Field(alias='POSTGRES_PORT')
    db_pool_size: int
    db_max_overflow: int
    db_pool_pre_ping: bool

    redis_host: str
    redis_port: str

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def redis_url(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'
