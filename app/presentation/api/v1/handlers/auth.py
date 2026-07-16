from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.auth.commands import LoginCommand
from app.application.auth.use_cases.login import LoginUseCase
from app.domain.auth.exceptions import IncorrectEmailOrPasswordError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.schemas.auth import JWTOutSchema, LoginInSchema

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
