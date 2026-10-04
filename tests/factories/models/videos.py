import secrets
from datetime import UTC, date, datetime

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.core.configs import settings
from app.domain.common.enums import ReactionTypeEnum
from app.domain.videos.constants import VIDEO_VIEWS_LIMIT_PER_DAY
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.infrastructure.sqlalchemy.models import (
    VideoCommentORM,
    VideoHistoryItemORM,
    VideoORM,
    VideoReactionORM,
    VideoViewORM,
)
from app.utils.datetime import get_current_utc_date, get_current_utc_datetime
from app.utils.videos import generate_video_id
from tests.factories.base import BaseORMFactory


class VideoORMFactory(BaseORMFactory[VideoORM], SQLAlchemyFactory[VideoORM]):
    @classmethod
    def id(cls) -> str:
        return generate_video_id()

    @classmethod
    def created_at(cls) -> datetime:
        return cls.__faker__.date_time(UTC)

    @classmethod
    def title(cls) -> str:
        return cls.__faker__.text(max_nb_chars=100)

    @classmethod
    def privacy_status(cls) -> str:
        return cls.__random__.choice([status.value for status in VideoPrivacyStatusEnum])

    @classmethod
    def upload_status(cls) -> str:
        return cls.__random__.choice([status.value for status in VideoUploadStatusEnum])

    @classmethod
    def s3_key(cls) -> str:
        return f'{settings.s3_videos_key_prefix}/{secrets.token_hex(5)}_test.mp4'

    @classmethod
    def upload_id(cls) -> str:
        return secrets.token_hex(16)


class VideoViewORMFactory(BaseORMFactory[VideoViewORM], SQLAlchemyFactory[VideoViewORM]):
    @classmethod
    def views_count(cls) -> int:
        return cls.__random__.choice(range(1, VIDEO_VIEWS_LIMIT_PER_DAY + 1))

    @classmethod
    def created_at(cls) -> date:
        return get_current_utc_date()


class VideoReactionORMFactory(BaseORMFactory[VideoReactionORM], SQLAlchemyFactory[VideoReactionORM]):
    @classmethod
    def reaction_type(cls) -> str:
        return cls.__random__.choice([ReactionTypeEnum.NEGATIVE.value, ReactionTypeEnum.POSITIVE.value])

    @classmethod
    def created_at(cls) -> date:
        return get_current_utc_datetime()


class VideoCommentORMFactory(BaseORMFactory[VideoCommentORM], SQLAlchemyFactory[VideoCommentORM]):
    @classmethod
    def created_at(cls) -> date:
        return get_current_utc_datetime()

    @classmethod
    def reply_comment_id(cls) -> None:
        return None


class VideoHistoryItemORMFactory(BaseORMFactory[VideoHistoryItemORM], SQLAlchemyFactory[VideoHistoryItemORM]):
    @classmethod
    def created_at(cls) -> date:
        return get_current_utc_datetime()

    @classmethod
    def video_id(cls) -> str:
        return generate_video_id()
