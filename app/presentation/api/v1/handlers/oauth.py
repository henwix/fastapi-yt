from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from app.application.oauth.commands import OAuthConvertCodeCommand
from app.application.oauth.queries import OAuthGetLoginUrlQuery
from app.application.oauth.use_cases.convert_code import OAuthConvertCodeUseCase
from app.application.oauth.use_cases.get_login_url import OAuthGetLoginUrlUseCase
from app.domain.channels.exceptions import (
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelWithEmailAlreadyExistsError,
)
from app.domain.oauth.enums import OAuthProviderEnum
from app.domain.oauth.exceptions import (
    OAuthInvalidCodeError,
    OAuthInvalidStateError,
    OAuthProviderAlreadyConnectedError,
    OAuthProviderEmailNotVerifiedError,
    OAuthProviderRequestError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import OptionalCurrentChannelID
from app.presentation.api.v1.schemas.requests.oauth import OAuthConvertCodeInSchema
from app.presentation.api.v1.schemas.responses.auth import JWTOutSchema
from app.presentation.api.v1.schemas.responses.oauth import OAuthLoginUrlOutSchema

router = APIRouter(
    prefix='/oauth',
    tags=['OAuth'],
    route_class=DishkaRoute,
)


@router.get(path='/login_url/{provider}')
async def get_login_url(
    provider: OAuthProviderEnum,
    use_case: FromDishka[OAuthGetLoginUrlUseCase],
) -> OAuthLoginUrlOutSchema:
    query = OAuthGetLoginUrlQuery(provider=provider)
    login_url = await use_case.execute(query=query)
    return OAuthLoginUrlOutSchema(login_url=login_url)


@router.post(
    path='/convert_code/{provider}',
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
