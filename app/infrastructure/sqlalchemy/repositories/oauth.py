from typing import NoReturn

from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProvidersEnum
from app.domain.oauth.repository import IOAuthAccountRepo
from app.infrastructure.sqlalchemy.models.oauth import OAuthAccountORM
from app.infrastructure.sqlalchemy.repositories.base import SARepository


class SAOAuthAccountRepo(SARepository, IOAuthAccountRepo):
    def _parse_db_error(self, error: DBAPIError, oauth_account: OAuthAccount) -> NoReturn: ...

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
        provider: OAuthProvidersEnum,
    ) -> OAuthAccount | None:
        stmt = select(OAuthAccountORM).where(
            OAuthAccountORM.provider_uid == uid,
            OAuthAccountORM.provider == provider.value,
        )
        result = await self._session.execute(statement=stmt)
        oauth_account = result.scalar_one_or_none()
        return oauth_account.to_entity() if oauth_account is not None else None
