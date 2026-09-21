from polyfactory.factories import DataclassFactory

from app.application.posts.queries import GetChannelPostsQuery, GetPostQuery, PostsSorting


class GetPostQueryFactory(DataclassFactory[GetPostQuery]):
    __model__ = GetPostQuery


class PostsSortingFactory(DataclassFactory[PostsSorting]):
    __model__ = PostsSorting


class GetChannelPostsQueryFactory(DataclassFactory[GetChannelPostsQuery]):
    __model__ = GetChannelPostsQuery
