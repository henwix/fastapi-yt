from dataclasses import dataclass

from app.application.common.dto.base import DTO


@dataclass(kw_only=True)
class CleanupResultDTO(DTO):
    total_deleted: int
    total_failed: int
