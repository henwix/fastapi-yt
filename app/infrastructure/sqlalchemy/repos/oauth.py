from typing import NoReturn

from sqlalchemy import select
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
                    current_channel_id=oauth_account.channel_id,
                    provider=oauth_account.provider,
                )
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
