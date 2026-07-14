from abc import ABC, abstractmethod

from app.application.videos.dto import DetailedVideoDTO


class IVideoReader(ABC):
    @abstractmethod
    async def try_get_detailed_by_id(self, id: str) -> DetailedVideoDTO: ...
