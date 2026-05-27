from .database import DatabaseSettings
from .general import GeneralSettings


class Settings(
    DatabaseSettings,
    GeneralSettings,
): ...


settings = Settings()
