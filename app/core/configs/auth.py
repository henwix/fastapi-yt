from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    jwt_access_secret_key: str
    jwt_refresh_secret_key: str
    jwt_algorithm: str
    jwt_access_exp_days: int
    jwt_refresh_exp_days: int
    auth_send_activation_email: bool
    frontend_activation_path: str
    frontend_set_email_confirm_path: str
    frontend_reset_password_confirm_path: str
