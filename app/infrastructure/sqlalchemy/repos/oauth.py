from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import OAuthProviderAlreadyConnectedError
from app.domain.oauth.repo import IOAuthAccountRepo
from app.infrastructure.sqlalchemy.models.oauth import OAuthAccountORM
from app.infrastructure.sqlalchemy.repos.base import SARepo


class SAOAuthAccountRepo(SARepo, IOAuthAccountRepo):
    def _parse_db_error(self, error: DBAPIError, oauth_account: OAuthAccount) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

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
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
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
        result = await self._session.execute(statement=stmt)
        oauth_account = result.scalar_one_or_none()
        return oauth_account.to_entity() if oauth_account is not None else None

    async def get_connected_for_update(self, channel_id: UUID) -> list[OAuthAccount]:
        stmt = (
            select(OAuthAccountORM)
            .with_for_update()
            .where(
                OAuthAccountORM.channel_id == channel_id,
            )
        )
        result = await self._session.execute(statement=stmt)
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
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
