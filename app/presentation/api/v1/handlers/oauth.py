from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.oauth.commands import OAuthConvertCodeCommand, OAuthDisconnectAccountCommand
from app.application.oauth.queries import OAuthGetConnectedAccountsQuery, OAuthGetLoginUrlQuery
from app.application.oauth.use_cases.convert_code import OAuthConvertCodeUseCase
from app.application.oauth.use_cases.disconnect_account import OAuthDisconnectAccountUseCase
from app.application.oauth.use_cases.get_connected_accounts import OAuthGetConnectedAccountsUseCase
from app.application.oauth.use_cases.get_login_url import OAuthGetLoginUrlUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
)
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import (
    OAuthAccountNotConnectedError,
    OAuthAccountUnableToDisconnectError,
    OAuthInvalidCodeError,
    OAuthInvalidStateError,
    OAuthNoAccountsConnectedError,
    OAuthProviderAlreadyConnectedError,
    OAuthProviderEmailNotVerifiedError,
    OAuthProviderRequestError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.schemas.requests.oauth import OAuthConvertCodeInSchema
from app.presentation.api.v1.schemas.responses.auth import JWTOutSchema
from app.presentation.api.v1.schemas.responses.oauth import OAuthAccountOutSchema, OAuthLoginUrlOutSchema

router = APIRouter(
    prefix='/oauth',
    tags=['OAuth'],
    route_class=DishkaRoute,
)


@router.get(
    path='/{provider}/login_url',
    summary='Get OAuth Login Url',
)
async def get_login_url(
    provider: OAuthProviderEnum,
    use_case: FromDishka[OAuthGetLoginUrlUseCase],
) -> OAuthLoginUrlOutSchema:
    query = OAuthGetLoginUrlQuery(provider=provider)
    login_url = await use_case.execute(query=query)
    return OAuthLoginUrlOutSchema(login_url=login_url)


@router.post(
    path='/{provider}/code',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'model': JWTOutSchema,
            'description': 'Returns JWT tokens if a new channel was created or an existing one was logged in to',
        },
        status.HTTP_204_NO_CONTENT: {
            'description': 'Returns 204 if the OAuth provider successfully connected to your channel'
        },
        status.HTTP_400_BAD_REQUEST: error_response(
            OAuthInvalidStateError,
            OAuthInvalidCodeError,
            OAuthProviderEmailNotVerifiedError,
            OAuthProviderAlreadyConnectedError,
            ChannelWithEmailAlreadyExistsError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            OAuthProviderRequestError,
        ),
    },
    summary='Convert OAuth Code',
)
async def convert_code(
    current_channel_id: OptionalCurrentChannelID,
    provider: OAuthProviderEnum,
    schema: OAuthConvertCodeInSchema,
    use_case: FromDishka[OAuthConvertCodeUseCase],
    response: Response,
) -> None | JWTOutSchema:
    command = OAuthConvertCodeCommand(
        current_channel_id=current_channel_id,
        provider=provider,
        **schema.model_dump(),
    )
    result = await use_case.execute(command=command)
    if result is None:
        response.status_code = status.HTTP_204_NO_CONTENT
        return result
    return JWTOutSchema(**result)


@router.get(
    path='/accounts',
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundByIdError),
    },
    summary='Get OAuth Connected Accounts',
)
async def get_oauth_connected_accounts(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[OAuthGetConnectedAccountsUseCase],
) -> list[OAuthAccountOutSchema]:
    query = OAuthGetConnectedAccountsQuery(current_channel_id=current_channel_id)
    accounts = await use_case.execute(query=query)
    return [OAuthAccountOutSchema.from_dto(dto=account) for account in accounts]


@router.delete(
    path='/{provider}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Disconnect OAuth Account',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            OAuthAccountUnableToDisconnectError,
        ),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            OAuthNoAccountsConnectedError,
            OAuthAccountNotConnectedError,
        ),
    },
)
async def disconnect_oauth_account(
    current_channel_id: CurrentChannelID,
    provider: OAuthProviderEnum,
    use_case: FromDishka[OAuthDisconnectAccountUseCase],
):
    command = OAuthDisconnectAccountCommand(
        current_channel_id=current_channel_id,
        provider=provider,
    )
    await use_case.execute(command=command)
