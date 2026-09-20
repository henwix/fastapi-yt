from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_user: str = Field(default='postgres', alias='POSTGRES_USER')
    db_password: str = Field(default='postgres', alias='POSTGRES_PASSWORD')
    db_name: str = Field(default='postgres', alias='POSTGRES_DB')
    db_host: str = Field(default='postgres', alias='POSTGRES_HOST')
    db_port: int = Field(default=5432, alias='POSTGRES_PORT')

    db_pool_size: int = 50
    db_max_overflow: int = 10
    db_pool_pre_ping: bool = True

    redis_host: str = 'redis'
    redis_port: int = 6379

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def redis_url(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'
