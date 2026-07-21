from datetime import UTC, datetime
from random import Random
from uuid import uuid4

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.configs import settings
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.infrastructure.sqlalchemy.models.videos import VideoORM
from app.utils.videos import generate_video_id


class VideoORMFactory(SQLAlchemyFactory[VideoORM]):
    __set_relationships__ = False
    __random__ = Random()
    __faker__ = Faker()

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
        return f'{settings.s3_videos_key_prefix}/{uuid4().hex[:10]}_test.mp4'

    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> VideoORM:
        obj = cls.build(**kwargs)
        session.add(obj)
        await session.commit()
        return obj

    @classmethod
    async def create_batch(cls, session: AsyncSession, size: int, **kwargs) -> list[VideoORM]:
        objects = cls.batch(size=size, **kwargs)
        session.add_all(objects)
        await session.commit()
        return objects
