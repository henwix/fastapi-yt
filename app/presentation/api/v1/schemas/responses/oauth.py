from pydantic import HttpUrl

from app.presentation.api.v1.schemas.base import BaseSchema


class OAuthLoginUrlOutSchema(BaseSchema):
    login_url: HttpUrl
