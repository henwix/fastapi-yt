from polyfactory.factories import DataclassFactory

from app.application.posts.queries import GetPostQuery, GetPostsQuery, PostsSorting


class GetPostQueryFactory(DataclassFactory[GetPostQuery]):
    __model__ = GetPostQuery


class PostsSortingFactory(DataclassFactory[PostsSorting]):
    __model__ = PostsSorting


class GetPostsQueryFactory(DataclassFactory[GetPostsQuery]):
    __model__ = GetPostsQuery
