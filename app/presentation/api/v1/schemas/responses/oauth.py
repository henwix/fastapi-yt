from datetime import datetime

from pydantic import HttpUrl

from app.application.oauth.dto import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class OAuthLoginUrlOutSchema(BaseSchema):
    login_url: HttpUrl


class OAuthAccountOutSchema(BaseSchema):
    provider: OAuthProviderEnum
    created_at: datetime

    @staticmethod
    def from_dto(dto: OAuthAccount) -> OAuthAccountOutSchema:
        return OAuthAccountOutSchema(
            provider=dto.provider,
            created_at=dto.created_at,
        )
