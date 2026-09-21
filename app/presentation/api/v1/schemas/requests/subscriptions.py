from app.application.common.sorting import SortingOrderEnum
from app.application.subscriptions.queries import SubscriptionsSortingFieldsEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class SubscriptionsSortingParamsSchema(BaseSchema):
    sort_by: SubscriptionsSortingFieldsEnum = SubscriptionsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
