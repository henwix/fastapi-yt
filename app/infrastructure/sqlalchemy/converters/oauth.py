from sqlalchemy import RowMapping

from app.application.oauth.dto import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum


def convert_row_to_oauth_account_dto(row: RowMapping) -> OAuthAccount:
    return OAuthAccount(
        provider=OAuthProviderEnum(row.provider),
        created_at=row.created_at,
    )
