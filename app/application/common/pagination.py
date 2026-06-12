from dataclasses import dataclass

from app.domain.common.constants import Empty


@dataclass(kw_only=True, frozen=True)
class CursorPagination:
    cursor: str | Empty = Empty.UNSET
    per_page: int
