from fastapi import APIRouter, status

from app.application.commands.channels import CreateChannelCommand
from app.application.use_cases.channels.create_channel import CreateChannelUseCase
from app.presentation.api.v1.di.container import PunqContainer
from app.presentation.api.v1.schemas.channels import CreateChannelSchema, GetChannelSchema

router = APIRouter()


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    schema: CreateChannelSchema,
    container: PunqContainer,
) -> GetChannelSchema:
    use_case: CreateChannelUseCase = container.resolve(CreateChannelUseCase)
    command = CreateChannelCommand(**schema.model_dump())
    channel = await use_case.execute(command=command)
    return GetChannelSchema.from_entity(entity=channel)
