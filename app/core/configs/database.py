from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_user: str = Field(alias='POSTGRES_USER')
    db_password: str = Field(alias='POSTGRES_PASSWORD')
    db_name: str = Field(alias='POSTGRES_DB')
    db_host: str = Field(alias='POSTGRES_HOST')
    db_port: int = Field(alias='POSTGRES_PORT')

    redis_host: str = Field(alias='REDIS_HOST')
    redis_port: str = Field(alias='REDIS_PORT')

    @property
    def db_url(self) -> str:
        return f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'

    @property
    def redis_url(self) -> str:
        return f'redis://{self.redis_host}:{self.redis_port}'
