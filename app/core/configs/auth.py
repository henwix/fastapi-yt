from pydantic_settings import BaseSettings


class AuthSettings(BaseSettings):
    jwt_access_secret_key: str = '123'
    jwt_refresh_secret_key: str = '456'
    jwt_algorithm: str = 'HS256'
    jwt_access_exp_minutes: int = 15
    jwt_refresh_exp_days: int = 7
    jwt_rotate_refresh_token: bool = True

    auth_send_activation_email: bool = False

    frontend_activation_path: str = 'auth/activation'
    frontend_set_email_confirm_path: str = 'auth/email/confirm'
    frontend_reset_password_confirm_path: str = 'auth/password/reset/confirm'
    frontend_login_email_confirm_path: str = 'auth/login/email/confirm'
