from pydantic_settings import BaseSettings


class S3Settings(BaseSettings):
    s3_access_key: str = '123'
    s3_secret_key: str = '123'
    s3_endpoint: str = '123'

    s3_public_bucket_name: str = '123'
    s3_public_bucket_url: str = '123'
    s3_private_bucket_name: str = '123'

    s3_channel_avatars_key_prefix: str = 'channel_avatars'
    s3_tmp_channel_avatars_key_prefix: str = 'tml/channel_avatars'
    s3_video_thumbnails_key_prefix: str = 'video_thumbnails'
    s3_tmp_video_thumbnails_key_prefix: str = 'tmp/video_thumbnails'
    s3_videos_key_prefix: str = 'videos'

    s3_connect_timeout: int = 5
    s3_read_timeout: int = 10
    s3_max_pool_connections: int = 10
    s3_retries_max_attempts: int = 3
