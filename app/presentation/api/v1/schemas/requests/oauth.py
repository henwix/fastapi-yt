from app.presentation.api.v1.schemas.base import BaseSchema


class OAuthConvertCodeInSchema(BaseSchema):
    code: str
    state: str
