from pydantic_settings import BaseSettings


class CleanupsSettings(BaseSettings):
    channel_deletion_retention_days: int = 7
    files_per_cleanup_batch: int = 500
    videos_per_cleanup_batch: int = 250
    incomplete_video_upload_expiration_days: int = 1
