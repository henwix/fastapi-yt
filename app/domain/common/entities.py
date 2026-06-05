from dataclasses import dataclass, field
from uuid import UUID, uuid7


@dataclass
class BaseEntity:
    id: UUID = field(default_factory=uuid7)
