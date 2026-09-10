from dataclasses import dataclass


@dataclass
class BaseValueObject[VT]:
    value: VT

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        """Validate value object"""

    def to_raw(self) -> VT:
        return self.value
