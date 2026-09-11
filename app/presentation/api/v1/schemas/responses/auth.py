from app.application.common.dto.jwt import JWTTokens
from app.presentation.api.v1.schemas.base import BaseSchema
from app.presentation.api.v1.schemas.responses.channels import ChannelOutSchema


class JWTTokensOutSchema(BaseSchema):
    access: str
    refresh: str

    @staticmethod
    def from_dto(dto: JWTTokens) -> JWTTokensOutSchema:
        return JWTTokensOutSchema(
            access=dto.access.token,
            refresh=dto.refresh.token,
        )


class RegisterChannelOutSchema(BaseSchema):
    channel: ChannelOutSchema
    tokens: JWTTokensOutSchema
    activation_required: bool
