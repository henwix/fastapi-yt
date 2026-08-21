from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.auth.commands import (
    ActivateChannelCommand,
    LoginChannelCommand,
    RegisterChannelCommand,
    ResendChannelActivationCodeCommand,
    ResetChannelPasswordCommand,
    ResetChannelPasswordConfirmCommand,
    SetChannelEmailCommand,
    SetChannelEmailConfirmCommand,
    SetChannelPasswordCommand,
)
from app.application.auth.use_cases.activate_channel import ActivateChannelUseCase
from app.application.auth.use_cases.login_channel import LoginChannelUseCase
from app.application.auth.use_cases.register_channel import RegisterChannelUseCase
from app.application.auth.use_cases.resend_channel_activation import ResendChannelActivationCodeUseCase
from app.application.auth.use_cases.reset_channel_password import ResetChannelPasswordUseCase
from app.application.auth.use_cases.reset_channel_password_confirm import ResetChannelPasswordConfirmUseCase
from app.application.auth.use_cases.set_channel_email import SetChannelEmailUseCase
from app.application.auth.use_cases.set_channel_email_confirm import SetChannelEmailConfirmUseCase
from app.application.auth.use_cases.set_channel_password import SetChannelPasswordUseCase
from app.domain.auth.exceptions import (
    ChannelAlreadyActivatedError,
    ChannelEmailAlreadyAssociatedWithThisAcccountError,
    ChannelInvalidEmailCodeError,
    ChannelInvalidEmailUIDError,
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
    ChannelWithSlugAlreadyExistsError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.requests.auth import (
    ActivateChannelInSchema,
    LoginInSchema,
    RegisterChannelInSchema,
    ResetChannelPasswordConfirmInSchema,
    ResetChannelPasswordInSchema,
    SetChannelEmailConfirmInSchema,
    SetChannelEmailInSchema,
    SetChannelPasswordInSchema,
)
from app.presentation.api.v1.schemas.responses.auth import JWTOutSchema, RegisterChannelOutSchema
from app.presentation.api.v1.schemas.responses.channels import ChannelOutSchema

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    route_class=DishkaRoute,
)


@router.post(
    path='/register',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelWithEmailAlreadyExistsError,
            ChannelWithSlugAlreadyExistsError,
        )
    },
)
async def register_channel(
    schema: RegisterChannelInSchema,
    use_case: FromDishka[RegisterChannelUseCase],
) -> RegisterChannelOutSchema:
    command = RegisterChannelCommand(**schema.model_dump())
    channel, tokens, activation_required = await use_case.execute(command=command)
    return RegisterChannelOutSchema(
        channel=ChannelOutSchema.from_entity(entity=channel),
        tokens=JWTOutSchema(**tokens),
        activation_required=activation_required,
    )


@router.post(
    path='/login',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(IncorrectEmailOrPasswordError),
    },
)
async def login_channel(
    schema: LoginInSchema,
    use_case: FromDishka[LoginChannelUseCase],
) -> JWTOutSchema:
    command = LoginChannelCommand(**schema.model_dump())
    tokens = await use_case.execute(command=command)
    return JWTOutSchema(**tokens)


@router.post(
    path='/activate',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelAlreadyActivatedError,
            ChannelInvalidEmailCodeError,
            ChannelActivationFailedError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def activate_channel(
    current_channel_id: CurrentChannelID,
    schema: ActivateChannelInSchema,
    use_case: FromDishka[ActivateChannelUseCase],
) -> None:
    command = ActivateChannelCommand(
        current_channel_id=current_channel_id,
        **schema.model_dump(),
    )
    await use_case.execute(command=command)


@router.post(
    path='/resend_activation',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelAlreadyActivatedError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def resend_channel_activation_code(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[ResendChannelActivationCodeUseCase],
) -> None:
    command = ResendChannelActivationCodeCommand(current_channel_id=current_channel_id)
    await use_case.execute(command=command)


@router.post(
    path='/set_email',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelEmailAlreadyAssociatedWithThisAcccountError,
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
            ChannelInvalidEmailCodeError,
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
    path='/set_password',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
    },
)
async def set_channel_password(
    schema: SetChannelPasswordInSchema,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[SetChannelPasswordUseCase],
) -> None:
    command = SetChannelPasswordCommand(current_channel_id=current_channel_id, **schema.model_dump())
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
            ChannelInvalidEmailUIDError,
            ChannelInvalidEmailCodeError,
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
