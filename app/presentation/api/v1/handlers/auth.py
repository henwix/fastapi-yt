from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.auth.commands import (
    ActivateChannelCommand,
    LoginCommand,
    ResendChannelActivationCodeCommand,
    ResetChannelPasswordCommand,
    ResetChannelPasswordConfirmCommand,
    SetChannelEmailCommand,
    SetChannelEmailConfirmCommand,
)
from app.application.auth.use_cases.activate_channel import ActivateChannelUseCase
from app.application.auth.use_cases.login import LoginUseCase
from app.application.auth.use_cases.resend_channel_activation import ResendChannelActivationCodeUseCase
from app.application.auth.use_cases.reset_channel_password import ResetChannelPasswordUseCase
from app.application.auth.use_cases.reset_channel_password_confirm import ResetChannelPasswordConfirmUseCase
from app.application.auth.use_cases.set_channel_email import SetChannelEmailUseCase
from app.application.auth.use_cases.set_channel_email_confirm import SetChannelEmailConfirmUseCase
from app.domain.auth.exceptions import (
    ChannelActivationDisabledError,
    ChannelActivationInvalidCodeError,
    ChannelActivationInvalidIdError,
    ChannelResetPasswordInvalidCodeError,
    ChannelResetPasswordInvalidIdError,
    ChannelSetEmailInvalidCodeError,
    IncorrectEmailOrPasswordError,
    JWTExpiredTokenError,
    JWTInvalidTokenError,
    NotAuthenticatedError,
)
from app.domain.channels.exceptions import (
    ChannelActivationFailedError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.requests.auth import (
    ActivateChannelInSchema,
    LoginInSchema,
    ResendChannelActivationCodeInSchema,
    ResetChannelPasswordConfirmInSchema,
    ResetChannelPasswordInSchema,
    SetChannelEmailConfirmInSchema,
    SetChannelEmailInSchema,
)
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
        status.HTTP_403_FORBIDDEN: error_response(ChannelActivationDisabledError),
    },
)
async def activate_channel(
    schema: ActivateChannelInSchema,
    use_case: FromDishka[ActivateChannelUseCase],
) -> None:
    command = ActivateChannelCommand(**schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/resend_activation',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            'description': 'If an channel with this email requires activation, a new activation email has been sent'
        },
        status.HTTP_403_FORBIDDEN: error_response(ChannelActivationDisabledError),
    },
)
async def resend_channel_activation_code(
    schema: ResendChannelActivationCodeInSchema,
    use_case: FromDishka[ResendChannelActivationCodeUseCase],
) -> None:
    command = ResendChannelActivationCodeCommand(**schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/set_email',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelWithEmailAlreadyExistsError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def set_channel_email(
    current_channel_id: CurrentChannelID,
    schema: SetChannelEmailInSchema,
    use_case: FromDishka[SetChannelEmailUseCase],
) -> None:
    command = SetChannelEmailCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/set_email_confirm',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelSetEmailInvalidCodeError,
            ChannelWithEmailAlreadyExistsError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def set_channel_email_confirm(
    current_channel_id: CurrentChannelID,
    schema: SetChannelEmailConfirmInSchema,
    use_case: FromDishka[SetChannelEmailConfirmUseCase],
) -> None:
    command = SetChannelEmailConfirmCommand(current_channel_id=current_channel_id, **schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/reset_password',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {'description': 'If an channel with this email exists, a new email has been sent'},
    },
)
async def reset_channel_password(
    schema: ResetChannelPasswordInSchema,
    use_case: FromDishka[ResetChannelPasswordUseCase],
) -> None:
    command = ResetChannelPasswordCommand(**schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/reset_password_confirm',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelResetPasswordInvalidIdError,
            ChannelResetPasswordInvalidCodeError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def reset_channel_password_confirm(
    schema: ResetChannelPasswordConfirmInSchema,
    use_case: FromDishka[ResetChannelPasswordConfirmUseCase],
) -> None:
    command = ResetChannelPasswordConfirmCommand(**schema.model_dump())
    await use_case.execute(command=command)
