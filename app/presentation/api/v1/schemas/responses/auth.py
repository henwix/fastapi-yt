from app.presentation.api.v1.schemas.base import BaseSchema
from app.presentation.api.v1.schemas.responses.channels import ChannelOutSchema


class JWTOutSchema(BaseSchema):
    access: str
    refresh: str


class RegisterChannelOutSchema(BaseSchema):
    channel: ChannelOutSchema
    activation_required: bool
