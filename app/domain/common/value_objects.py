from dataclasses import dataclass
from datetime import datetime

from app.utils.datetime import get_current_utc_datetime


@dataclass
class BaseValueObject[VT]:
    value: VT

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate value object"""

    def to_raw(self) -> VT:
        return self.value


class DeletionTime(BaseValueObject[datetime | None]):
    @staticmethod
    def create_deleted() -> DeletionTime:
        return DeletionTime(get_current_utc_datetime())

    @staticmethod
    def create_not_deleted() -> DeletionTime:
        return DeletionTime(None)

    def is_deleted(self) -> bool:
        return self.value is not None
