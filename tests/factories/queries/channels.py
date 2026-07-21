from polyfactory.factories import DataclassFactory

from app.application.channels.queries import GetChannelQuery


class GetChannelQueryFactory(DataclassFactory[GetChannelQuery]):
    __model__ = GetChannelQuery
