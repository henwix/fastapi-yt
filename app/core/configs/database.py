from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_user: str = Field(alias='POSTGRES_USER')
    db_password: str = Field(alias='POSTGRES_PASSWORD')
    db_name: str = Field(alias='POSTGRES_DB')
    db_host: str = Field(alias='POSTGRES_HOST')
    db_port: int = Field(alias='POSTGRES_PORT')
    db_url: str | None = None

    @model_validator(mode='after')
    def build_db_url(self) -> Self:
        if self.db_url is None:
            self.db_url = (
                f'postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
            )
        return self
