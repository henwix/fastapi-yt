from polyfactory.factories import DataclassFactory

from app.application.videos.queries import GetVideoCommentsQuery


class GetVideoCommentsQueryFactory(DataclassFactory[GetVideoCommentsQuery]):
    __model__ = GetVideoCommentsQuery
