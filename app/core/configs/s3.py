from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    s3_access_key: str
    s3_secret_key: str
    s3_endpoint: str
    s3_public_bucket_name: str
    s3_public_bucket_url: str
    s3_private_bucket_name: str
    s3_avatars_key_prefix: str
    s3_tmp_avatars_key_prefix: str
    s3_videos_key_prefix: str
    s3_connect_timeout: int
    s3_read_timeout: int
    s3_max_pool_connections: int
    s3_retries_max_attempts: int
