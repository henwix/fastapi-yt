from dataclasses import dataclass

from app.application.posts.dto import DetailedPost
from app.application.posts.interfaces import IPostReader
from app.application.posts.queries import GetPostQuery


@dataclass
class GetPostUseCase:
    _post_reader: IPostReader

    async def execute(self, query: GetPostQuery) -> DetailedPost:
        return await self._post_reader.try_get_detailed_by_id(id=query.post_id)
