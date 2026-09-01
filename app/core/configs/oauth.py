from pydantic_settings import BaseSettings


class OAuthSettings(BaseSettings):
    oauth_redirect_path: str
    oauth_github_client_id: str
    oauth_github_client_secret: str
    oauth_google_client_id: str
    oauth_google_client_secret: str
