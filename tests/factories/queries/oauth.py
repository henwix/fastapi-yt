from polyfactory.factories import DataclassFactory

from app.application.oauth.queries import GenerateOAuthLoginUrlQuery, GetOAuthConnectedAccountsQuery


class GenerateOAuthLoginUrlQueryFactory(DataclassFactory[GenerateOAuthLoginUrlQuery]):
    __model__ = GenerateOAuthLoginUrlQuery


class GetOAuthConnectedAccountsQueryFactory(DataclassFactory[GetOAuthConnectedAccountsQuery]):
    __model__ = GetOAuthConnectedAccountsQuery
