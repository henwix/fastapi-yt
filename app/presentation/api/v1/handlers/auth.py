from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.auth.commands import ActivateChannelCommand, LoginCommand
from app.application.auth.use_cases.activate_channel import ActivateChannelUseCase
from app.application.auth.use_cases.login import LoginUseCase
from app.domain.auth.exceptions import (
    ChannelActivationInvalidCodeError,
    ChannelActivationInvalidIdError,
    IncorrectEmailOrPasswordError,
)
from app.domain.channels.exceptions import ChannelActivationFailedError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.schemas.requests.auth import ActivateChannelInSchema, LoginInSchema
from app.presentation.api.v1.schemas.responses.auth import JWTOutSchema

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    route_class=DishkaRoute,
)


@router.post(
    path='/login',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(IncorrectEmailOrPasswordError),
    },
)
async def login(
    schema: LoginInSchema,
    use_case: FromDishka[LoginUseCase],
) -> JWTOutSchema:
    command = LoginCommand(**schema.model_dump())
    tokens = await use_case.execute(command=command)
    return JWTOutSchema(**tokens)


@router.post(
    path='/activate',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelActivationInvalidIdError,
            ChannelActivationInvalidCodeError,
            ChannelActivationFailedError,
        ),
    },
)
async def activate_channel(
    schema: ActivateChannelInSchema,
    use_case: FromDishka[ActivateChannelUseCase],
) -> None:
    command = ActivateChannelCommand(**schema.model_dump())
    await use_case.execute(command=command)
