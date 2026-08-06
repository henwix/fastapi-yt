from polyfactory.factories import DataclassFactory

from app.application.video_views.commands import CreateVideoViewCommand
from app.utils.videos import generate_video_id


class CreateVideoViewCommandFactory(DataclassFactory[CreateVideoViewCommand]):
    __model__ = CreateVideoViewCommand

    @classmethod
    def video_id(cls) -> str:
        return generate_video_id()
