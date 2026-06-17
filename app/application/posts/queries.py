from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class GetPostQuery:
    post_id: UUID
