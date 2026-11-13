from pydantic_settings import BaseSettings


class CleanupsSettings(BaseSettings):
    channel_deletion_retention_days: int = 7
    video_incomplete_upload_expiration_days: int = 1
    files_cleanups_batch_limit: int = 500
    videos_cleanup_batch_limit: int = 250

    channels_purging_batch_limit: int = 250
    videos_purging_batch_limit: int = 500
    files_purging_batch_limit: int = 1000
    channels_purging_lock_exp_minutes: int = 60
