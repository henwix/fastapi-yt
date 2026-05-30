from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    jwt_access_secret_key: str
    jwt_refresh_secret_key: str
    jwt_algorithm: str
    jwt_access_exp_days: int
    jwt_refresh_exp_days: int
