from pydantic_settings import BaseSettings


class OAuthSettings(BaseSettings):
    oauth_github_redirect_path: str
    oauth_github_client_id: str
    oauth_github_client_secret: str
