from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class LoginCommand:
    email: str
    password: str


@dataclass(kw_only=True, frozen=True)
class ActivateChannelCommand:
    code: str
    uid: str


@dataclass(kw_only=True, frozen=True)
class ResendChannelActivationCodeCommand:
    email: str


@dataclass(kw_only=True, frozen=True)
class SetChannelEmailCommand:
    current_channel_id: UUID
    new_email: str


@dataclass(kw_only=True, frozen=True)
class SetChannelEmailConfirmCommand:
    current_channel_id: UUID
    code: str


@dataclass(kw_only=True, frozen=True)
class ResetChannelPasswordCommand:
    email: str


@dataclass(kw_only=True, frozen=True)
class ResetChannelPasswordConfirmCommand:
    code: str
    uid: str
    new_password: str
