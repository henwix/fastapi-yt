from polyfactory.factories import DataclassFactory

from app.application.videos.queries import GetVideoQuery
from app.utils.videos import generate_video_id


class GetVideoQueryFactory(DataclassFactory[GetVideoQuery]):
    __model__ = GetVideoQuery

    @classmethod
    def video_id(cls) -> str:
        return generate_video_id()
