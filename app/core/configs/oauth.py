from pydantic_settings import BaseSettings


class OAuthSettings(BaseSettings):
    oauth_redirect_path: str = 'oauth/convert_code'

    oauth_github_client_id: str = '123'
    oauth_github_client_secret: str = '123'
    oauth_google_client_id: str = '123'
    oauth_google_client_secret: str = '123'
