from pydantic import HttpUrl
from pydantic_settings import BaseSettings


class GeneralSettings(BaseSettings):
    app_name: str = 'FastAPI YouTube Backend'
    debug: bool = True
    logging_level: str = 'DEBUG'
    cors_allowed_origins: list[str] = []
    frontend_origin: HttpUrl = HttpUrl('http://localhost/')
