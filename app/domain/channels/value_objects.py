import re
from dataclasses import dataclass

from app.domain.channels.constants import CHANNEL_EMAIL_MAX_LENGTH, CHANNEL_NAME_MAX_LENGTH, CHANNEL_SLUG_MAX_LENGTH
from app.domain.channels.exceptions import (
    ChannelEmailTooLongError,
    ChannelInvalidEmailFormatError,
    ChannelInvalidSlugFormatError,
    ChannelSlugTooLongError,
)
from app.domain.common.constants import EMAIL_PATTERN, SLUG_PATTERN
from app.domain.common.value_objects import BaseValueObject


@dataclass(eq=False)
class Email(BaseValueObject):
    value: str

    def _validate(self) -> None:
        value = self.value.strip().lower()
        if not re.fullmatch(pattern=EMAIL_PATTERN, string=value):
            raise ChannelInvalidEmailFormatError(pattern=EMAIL_PATTERN, email=value)
        if len(value) > CHANNEL_EMAIL_MAX_LENGTH:
            raise ChannelEmailTooLongError(email=value, email_max_length=CHANNEL_EMAIL_MAX_LENGTH)
        self.value = value


@dataclass(eq=False)
class Slug(BaseValueObject):
    value: str

    def _validate(self) -> None:
        value = self.value.strip().lower()
        if not re.fullmatch(pattern=SLUG_PATTERN, string=value):
            raise ChannelInvalidSlugFormatError(pattern=SLUG_PATTERN, slug=value)
        if len(value) > CHANNEL_SLUG_MAX_LENGTH:
            raise ChannelSlugTooLongError(slug=value, slug_max_length=CHANNEL_SLUG_MAX_LENGTH)
        self.value = value


@dataclass(eq=False)
class Name(BaseValueObject):
    value: str

    def _validate(self) -> None:
        value = self.value.strip()
        if len(value) > CHANNEL_NAME_MAX_LENGTH:
            value = value[:100]
        self.value = value
