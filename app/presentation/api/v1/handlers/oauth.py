from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.oauth.commands import DisconnectOAuthAccountCommand, VerifyOAuthCodeCommand
from app.application.oauth.queries import GenerateOAuthLoginUrlQuery, GetOAuthConnectedAccountsQuery
from app.application.oauth.usecases import (
    DisconnectOAuthAccountUseCase,
    GenerateOAuthLoginUrlUseCase,
    GetOAuthConnectedAccountsUseCase,
    VerifyOAuthCodeUseCase,
)
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import (
    ChannelEmailAlreadyExistsError,
    ChannelEmailInvalidFormatError,
    ChannelEmailTooLongError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
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
    OAuthProviderReceivedInvalidResponseError,
    OAuthProviderRequestError,
    OAuthProviderResponseError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID, OptionalCurrentChannelID
from app.presentation.api.v1.schemas.requests.oauth import VerifyOAuthCodeInSchema
from app.presentation.api.v1.schemas.responses.auth import JWTTokensOutSchema
from app.presentation.api.v1.schemas.responses.oauth import OAuthAccountOutSchema, OAuthLoginUrlOutSchema

router = APIRouter(
    prefix='/oauth',
    tags=['OAuth'],
    route_class=DishkaRoute,
)


@router.get(
    path='/{oauth_provider}/login/url',
    summary='Generate OAuth Login Url',
)
async def generate_oauth_login_url(
    oauth_provider: OAuthProviderEnum,
    use_case: FromDishka[GenerateOAuthLoginUrlUseCase],
) -> OAuthLoginUrlOutSchema:
    query = GenerateOAuthLoginUrlQuery(provider=oauth_provider)
    login_url = await use_case.execute(query=query)
    return OAuthLoginUrlOutSchema(login_url=login_url)


@router.post(
    path='/{oauth_provider}/login/verify',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            'model': JWTTokensOutSchema,
            'description': 'Returns JWT tokens if a new channel was created or an existing one was logged in to',
        },
        status.HTTP_204_NO_CONTENT: {
            'description': 'Returns 204 if the OAuth provider successfully connected to your channel'
        },
        status.HTTP_400_BAD_REQUEST: error_response(
            OAuthInvalidStateError,
            OAuthInvalidCodeError,
            ChannelEmailInvalidFormatError,
            ChannelEmailTooLongError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(
            ChannelNotActiveError,
        ),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            ChannelEmailAlreadyExistsError,
            OAuthProviderEmailNotVerifiedError,
            OAuthProviderAlreadyConnectedError,
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: error_response(
            OAuthProviderRequestError,
        ),
        status.HTTP_502_BAD_GATEWAY: error_response(
            OAuthProviderResponseError,
            OAuthProviderReceivedInvalidResponseError,
        ),
    },
    summary='Verify OAuth Code',
)
async def verify_oauth_code(
    current_channel_id: OptionalCurrentChannelID,
    oauth_provider: OAuthProviderEnum,
    schema: VerifyOAuthCodeInSchema,
    use_case: FromDishka[VerifyOAuthCodeUseCase],
    response: Response,
) -> JWTTokensOutSchema | None:
    command = VerifyOAuthCodeCommand(
        current_channel_id=current_channel_id,
        provider=oauth_provider,
        **schema.model_dump(),
    )
    result = await use_case.execute(command=command)
    if result is None:
        response.status_code = status.HTTP_204_NO_CONTENT
        return result
    return JWTTokensOutSchema.from_dto(dto=result)


@router.get(
    path='/accounts',
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
    },
    summary='Get OAuth Connected Accounts',
)
async def get_oauth_connected_accounts(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[GetOAuthConnectedAccountsUseCase],
) -> list[OAuthAccountOutSchema]:
    query = GetOAuthConnectedAccountsQuery(current_channel_id=current_channel_id)
    accounts = await use_case.execute(query=query)
    return [OAuthAccountOutSchema.from_dto(dto=account) for account in accounts]


@router.delete(
    path='/{oauth_provider}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Disconnect OAuth Account',
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
            OAuthNoAccountsConnectedError,
            OAuthAccountNotConnectedError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            OAuthAccountUnableToDisconnectError,
        ),
    },
)
async def disconnect_oauth_account(
    current_channel_id: CurrentChannelID,
    oauth_provider: OAuthProviderEnum,
    use_case: FromDishka[DisconnectOAuthAccountUseCase],
) -> None:
    command = DisconnectOAuthAccountCommand(
        current_channel_id=current_channel_id,
        provider=oauth_provider,
    )
    await use_case.execute(command=command)
