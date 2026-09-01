from app.presentation.api.v1.schemas.base import BaseSchema


class OAuthVerifyCodeInSchema(BaseSchema):
    code: str
    state: str
