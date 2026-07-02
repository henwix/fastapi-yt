from polyfactory.factories import DataclassFactory

from app.application.subscriptions.queries import (
    GetSubscribersQuery,
    GetSubscriptionsQuery,
    SubscriptionsSorting,
)


class SubscriptionsSortingFactory(DataclassFactory[SubscriptionsSorting]):
    __model__ = SubscriptionsSorting


class GetSubscribersQueryFactory(DataclassFactory[GetSubscribersQuery]):
    __model__ = GetSubscribersQuery


class GetSubscriptionsQueryFactory(DataclassFactory[GetSubscriptionsQuery]):
    __model__ = GetSubscriptionsQuery
