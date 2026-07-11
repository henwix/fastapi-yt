from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.posts.queries import GetPostQuery
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class GetPostUseCase:
    _post_service: IPostService
    _transaction_manager: ITransactionManager

    async def execute(self, query: GetPostQuery) -> Post:
        async with self._transaction_manager:
            return await self._post_service.try_get_by_id(id=query.post_id)
