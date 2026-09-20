from pydantic_settings import BaseSettings


class EmailSettings(BaseSettings):
    email_username: str = '123'
    email_password: str = '123'
    email_from_name: str = '123'
    email_smtp_server: str = '123'
