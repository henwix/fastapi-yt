from polyfactory.factories import DataclassFactory

from app.application.oauth.queries import OAuthGetConnectedAccountsQuery, OAuthGetLoginUrlQuery


class OAuthGetLoginUrlQueryFactory(DataclassFactory[OAuthGetLoginUrlQuery]):
    __model__ = OAuthGetLoginUrlQuery


class OAuthGetConnectedAccountsQueryFactory(DataclassFactory[OAuthGetConnectedAccountsQuery]):
    __model__ = OAuthGetConnectedAccountsQuery
