from .database import DatabaseSettings
from .general import GeneralSettings


class Settings(
    GeneralSettings,
    DatabaseSettings,
): ...


settings = Settings()
