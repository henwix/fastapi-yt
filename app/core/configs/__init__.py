from pathlib import Path

from pydantic_settings import SettingsConfigDict

from app.core.configs.auth import AuthSettings
from app.core.configs.database import DatabaseSettings
from app.core.configs.general import GeneralSettings
from app.core.configs.s3 import S3Settings

BASE_DIR = Path(__name__).resolve().parent


class Settings(
    GeneralSettings,
    DatabaseSettings,
    AuthSettings,
    S3Settings,
):
    model_config = SettingsConfigDict(
        extra='ignore',
        env_file=BASE_DIR / '.env',
    )


settings = Settings()
