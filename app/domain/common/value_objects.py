from dataclasses import dataclass
from typing import Any


@dataclass
class BaseValueObject:
    value: Any

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None: ...

    def __eq__(self, value: object) -> bool:
        return self.value == value
