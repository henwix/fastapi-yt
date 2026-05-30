from app.core.configs.auth import AuthSettings
from app.core.configs.database import DatabaseSettings
from app.core.configs.general import GeneralSettings


class Settings(
    GeneralSettings,
    DatabaseSettings,
    AuthSettings,
): ...


settings = Settings()
