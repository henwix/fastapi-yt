from pydantic import Field
from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    s3_access_key: str = Field(alias='S3_ACCESS_KEY')
    s3_secret_key: str = Field(alias='S3_SECRET_KEY')
    s3_endpoint: str = Field(alias='S3_ENDPOINT')
    s3_public_bucket_name: str = Field(alias='S3_PUBLIC_BUCKET_NAME')
    s3_public_bucket_url: str = Field(alias='S3_PUBLIC_BUCKET_URL')
    s3_private_bucket_name: str = Field(alias='S3_PRIVATE_BUCKET_NAME')
    s3_avatars_key_prefix: str = Field(alias='S3_AVATARS_KEY_PREFIX')
    s3_videos_key_prefix: str = Field(alias='S3_VIDEOS_KEY_PREFIX')
