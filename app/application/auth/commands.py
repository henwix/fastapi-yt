from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class LoginCommand:
    email: str
    password: str
