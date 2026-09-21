from app.presentation.api.v1.schemas.base import BaseSchema


class VerifyOAuthCodeInSchema(BaseSchema):
    code: str
    state: str
