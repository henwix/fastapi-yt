from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status

from app.application.auth.commands import (
    ActivateChannelCommand,
    LoginWithPasswordCommand,
    LogoutCommand,
    RefreshJWTTokenCommand,
    RegisterChannelWithPasswordCommand,
    ResendChannelActivationCodeCommand,
    ResetChannelPasswordCommand,
    ResetChannelPasswordConfirmCommand,
    SetChannelEmailCommand,
    SetChannelEmailConfirmCommand,
    SetChannelPasswordCommand,
)
from app.application.auth.usecases import (
    ActivateChannelUseCase,
    LoginWithPasswordUseCase,
    LogoutUseCase,
    RefreshJWTTokenUseCase,
    RegisterChannelWithPasswordUseCase,
    ResendChannelActivationCodeUseCase,
    ResetChannelPasswordConfirmUseCase,
    ResetChannelPasswordUseCase,
    SetChannelEmailConfirmUseCase,
    SetChannelEmailUseCase,
    SetChannelPasswordUseCase,
)
from app.domain.auth.exceptions import (
    ChannelAlreadyActivatedError,
    ChannelEmailAlreadyAssociatedWithThisAcccountError,
    ChannelInvalidEmailCodeError,
    ChannelInvalidEmailUIDError,
    IncorrectEmailOrPasswordError,
    JWTTokenExpiredError,
    JWTTokenInvalidError,
    JWTTokenNotFoundError,
    NotAuthenticatedError,
)
from app.domain.channels.exceptions import (
    ChannelActivationFailedError,
    ChannelEmailAlreadyExistsError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelSlugAlreadyExistsError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID
from app.presentation.api.v1.schemas.requests.auth import (
    ActivateChannelInSchema,
    LoginWithPasswordInSchema,
    LogoutInSchema,
    RefreshJWTTokenInSchema,
    RegisterChannelWithPasswordInSchema,
    ResetChannelPasswordConfirmInSchema,
    ResetChannelPasswordInSchema,
    SetChannelEmailConfirmInSchema,
    SetChannelEmailInSchema,
    SetChannelPasswordInSchema,
)
from app.presentation.api.v1.schemas.responses.auth import JWTTokensOutSchema, RegisterChannelOutSchema
from app.presentation.api.v1.schemas.responses.channels import ChannelOutSchema

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    route_class=DishkaRoute,
)


@router.post(
    path='/register/password',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: error_response(
            ChannelEmailAlreadyExistsError,
            ChannelSlugAlreadyExistsError,
        ),
    },
)
async def register_channel_with_password(
    schema: RegisterChannelWithPasswordInSchema,
    use_case: FromDishka[RegisterChannelWithPasswordUseCase],
) -> RegisterChannelOutSchema:
    command = RegisterChannelWithPasswordCommand(**schema.model_dump())
    channel, tokens, activation_required = await use_case.execute(command=command)
    return RegisterChannelOutSchema(
        channel=ChannelOutSchema.from_entity(entity=channel),
        tokens=JWTTokensOutSchema.from_dto(dto=tokens),
        activation_required=activation_required,
    )


@router.post(
    path='/login/password',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            IncorrectEmailOrPasswordError,
        ),
    },
)
async def login_with_password(
    schema: LoginWithPasswordInSchema,
    use_case: FromDishka[LoginWithPasswordUseCase],
) -> JWTTokensOutSchema:
    command = LoginWithPasswordCommand(**schema.model_dump())
    tokens = await use_case.execute(command=command)
    return JWTTokensOutSchema.from_dto(dto=tokens)


@router.post(
    path='/token/refresh',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            JWTTokenNotFoundError,
        ),
    },
)
async def refresh_jwt_token(
    schema: RefreshJWTTokenInSchema,
    use_case: FromDishka[RefreshJWTTokenUseCase],
) -> JWTTokensOutSchema:
    command = RefreshJWTTokenCommand(**schema.model_dump())
    tokens = await use_case.execute(command=command)
    return JWTTokensOutSchema.from_dto(dto=tokens)


@router.post(
    path='/logout',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            JWTTokenNotFoundError,
        ),
    },
)
async def logout(
    schema: LogoutInSchema,
    use_case: FromDishka[LogoutUseCase],
) -> None:
    command = LogoutCommand(**schema.model_dump())
    await use_case.execute(command=command)


@router.post(
    path='/activation',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelInvalidEmailCodeError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            ChannelAlreadyActivatedError,
            ChannelActivationFailedError,
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
    path='/activation/resend',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            ChannelAlreadyActivatedError,
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
    path='/email',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            ChannelEmailAlreadyExistsError,
            ChannelEmailAlreadyAssociatedWithThisAcccountError,
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
    path='/email/confirm',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            ChannelInvalidEmailCodeError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            ChannelEmailAlreadyExistsError,
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
    path='/password',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTTokenExpiredError,
            JWTTokenInvalidError,
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
    path='/password/reset',
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
    path='/password/reset/confirm',
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
