from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete, select
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import OAuthProviderAlreadyConnectedError
from app.domain.oauth.repos import IOAuthAccountRepo
from app.infrastructure.sqlalchemy.models import OAuthAccountORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class OAuthAccountRepo(SQLAlchemyRepo, IOAuthAccountRepo):
    def _parse_db_error(self, error: DBAPIError, oauth_account: OAuthAccount) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'uq_channel_provider' | 'uq_provider_uid':
                raise OAuthProviderAlreadyConnectedError(
                    channel_id=oauth_account.channel_id,
                    provider=oauth_account.provider,
                ) from error
            case _:
                raise

    async def create(self, oauth_account: OAuthAccount) -> None:
        model = OAuthAccountORM.from_entity(entity=oauth_account)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, oauth_account=oauth_account)

    async def get_by_uid_and_provider(
        self,
        uid: str,
        provider: OAuthProviderEnum,
    ) -> OAuthAccount | None:
        stmt = select(OAuthAccountORM).where(
            OAuthAccountORM.provider_uid == uid,
            OAuthAccountORM.provider == provider.value,
        )
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        oauth_account = result.scalar_one_or_none()
        return oauth_account.to_entity() if oauth_account is not None else None

    async def get_connected(self, channel_id: UUID) -> list[OAuthAccount]:
        stmt = select(OAuthAccountORM).where(OAuthAccountORM.channel_id == channel_id)
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        connected_accounts = result.scalars()
        return [account.to_entity() for account in connected_accounts]

    async def delete_by_channel_id_and_provider(
        self,
        channel_id: UUID,
        provider: OAuthProviderEnum,
    ) -> bool:
        stmt = delete(OAuthAccountORM).where(
            OAuthAccountORM.channel_id == channel_id,
            OAuthAccountORM.provider == provider.value,
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0
