from typing import Self

from pydantic import BaseModel, ConfigDict, model_validator


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid',
    )


class BaseUpdateSchema(BaseSchema):
    @model_validator(mode='after')
    def empty_schema_validator(self) -> Self:
        if not self.model_fields_set:
            raise ValueError('At least one field must be provided')
        return self
