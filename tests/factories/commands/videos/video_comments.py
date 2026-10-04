from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.videos.commands import (
    CreateVideoCommentCommand,
    DeleteVideoCommentCommand,
    UpdateVideoCommentCommand,
)
from app.domain.common.constants import Empty
from app.utils.videos import generate_video_id


class CreateVideoCommentCommandFactory(DataclassFactory[CreateVideoCommentCommand]):
    __model__ = CreateVideoCommentCommand

    @classmethod
    def video_id(cls) -> str:
        return generate_video_id()

    @classmethod
    def reply_comment_id(cls) -> Empty:
        return Empty.UNSET


class DeleteVideoCommentCommandFactory(DataclassFactory[DeleteVideoCommentCommand]):
    __model__ = DeleteVideoCommentCommand


class UpdateVideoCommentCommandFactory(DataclassFactory[UpdateVideoCommentCommand]):
    __model__ = UpdateVideoCommentCommand
    __faker__ = Faker()

    @classmethod
    def text(cls) -> str:
        return cls.__faker__.text()
