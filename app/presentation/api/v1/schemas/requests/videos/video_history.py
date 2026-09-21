from app.application.common.sorting import SortingOrderEnum
from app.application.videos.queries import VideoHistorySortingFieldsEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class VideoHistorySortingParamsSchema(BaseSchema):
    sort_by: VideoHistorySortingFieldsEnum = VideoHistorySortingFieldsEnum.WATCHED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
