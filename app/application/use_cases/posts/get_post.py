from dataclasses import dataclass

from app.application.common.transaction_manager import ITransactionManager
from app.application.queries.posts import GetPostQuery
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class GetPostUseCase:
    post_service: IPostService
    transaction_manager: ITransactionManager

    async def execute(self, query: GetPostQuery) -> Post:
        async with self.transaction_manager:
            return await self.post_service.try_get_by_id(id=query.post_id)
