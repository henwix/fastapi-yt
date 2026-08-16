from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    email_username: str
    email_password: str
    email_from_name: str
    email_smtp_server: str
    email_send_activation_email: bool
