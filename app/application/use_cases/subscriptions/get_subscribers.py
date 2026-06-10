from dataclasses import dataclass

from app.application.queries.subscriptions import GetSubscribersQuery
from app.domain.subscriptions.entities import Subscription


@dataclass
class GetSubscribersUseCase:
    async def execute(self, query: GetSubscribersQuery) -> list[Subscription]: ...
