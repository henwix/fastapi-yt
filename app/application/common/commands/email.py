from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class SendChannelActivationCodeCommand:
    email: str
    name: str
    activation_url: str
    code: str


@dataclass(kw_only=True, frozen=True)
class SendChannelSetEmailCodeCommand:
    email: str
    name: str
    confirmation_url: str
    code: str


@dataclass(kw_only=True, frozen=True)
class SendChannelResetPasswordCodeCommand:
    email: str
    name: str
    confirmation_url: str
    code: str
    uid: str
