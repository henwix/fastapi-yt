from app.domain.common.enums import ReactionTypeEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class CreateVideoReactionInSchema(BaseSchema):
    reaction_type: ReactionTypeEnum
