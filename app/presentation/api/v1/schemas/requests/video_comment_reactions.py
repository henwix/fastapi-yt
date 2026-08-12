from app.domain.common.enums import ReactionTypeEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class CreateVideoCommentReactionInSchema(BaseSchema):
    reaction_type: ReactionTypeEnum
