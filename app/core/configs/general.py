from pydantic_settings import BaseSettings


class GeneralSettings(BaseSettings):
    app_name: str
    debug: bool
    logging_level: str
    cors_allowed_origins: list[str]
