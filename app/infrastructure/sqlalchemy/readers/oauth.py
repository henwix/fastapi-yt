from uuid import UUID

from sqlalchemy import select

from app.application.oauth.dto import OAuthAccount
from app.application.oauth.interfaces.reader import IOAuthAccountReader
from app.infrastructure.sqlalchemy.converters.oauth import convert_row_to_oauth_account_dto
from app.infrastructure.sqlalchemy.models.oauth import OAuthAccountORM
from app.infrastructure.sqlalchemy.readers.base import SAReader


class SAOAuthAccountReader(SAReader, IOAuthAccountReader):
    async def get_connected(self, channel_id: UUID) -> list[OAuthAccount]:
        stmt = select(
            OAuthAccountORM.provider,
            OAuthAccountORM.created_at,
        ).where(OAuthAccountORM.channel_id == channel_id)
        result = await self._session.execute(statement=stmt)
        rows = result.mappings().all()
        return [convert_row_to_oauth_account_dto(row=row) for row in rows]
