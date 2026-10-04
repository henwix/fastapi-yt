from polyfactory.factories import DataclassFactory

from app.application.videos.commands import CreateVideoReactionCommand, DeleteVideoReactionCommand
from app.utils.videos import generate_video_id


class CreateVideoReactionCommandFactory(DataclassFactory[CreateVideoReactionCommand]):
    __model__ = CreateVideoReactionCommand

    @classmethod
    def video_id(cls) -> str:
        return generate_video_id()


class DeleteVideoReactionCommandFactory(DataclassFactory[DeleteVideoReactionCommand]):
    __model__ = DeleteVideoReactionCommand

    @classmethod
    def video_id(cls) -> str:
        return generate_video_id()
