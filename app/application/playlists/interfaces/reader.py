from abc import ABC, abstractmethod
from uuid import UUID

from app.application.playlists.dto import DetailedPlaylistDTO


class IPlaylistReader(ABC):
    @abstractmethod
    async def try_get_detailed_by_id(self, id: UUID) -> DetailedPlaylistDTO: ...
