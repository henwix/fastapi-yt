from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from app.application.commands.channels import CreateChannelCommand
from app.application.use_cases.channels.create_channel import CreateChannelUseCase
from app.domain.channels.exceptions import ChannelWithEmailAlreadyExists, ChannelWithSlugAlreadyExists
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.schemas.channels import CreateChannelSchema, GetChannelSchema

router = APIRouter(
    prefix='/channels',
    tags=['Channels'],
    route_class=DishkaRoute,
)


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelWithEmailAlreadyExists,
            ChannelWithSlugAlreadyExists,
        )
    },
)
async def create_channel(
    schema: CreateChannelSchema,
    use_case: FromDishka[CreateChannelUseCase],
) -> GetChannelSchema:
    command = CreateChannelCommand(**schema.model_dump())
    channel = await use_case.execute(command=command)
    return GetChannelSchema.from_entity(entity=channel)
