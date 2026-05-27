from dataclasses import dataclass


@dataclass
class CreateChannelCommand:
    email: str
    name: str
    slug: str
    description: str
    country: str
    password: str
