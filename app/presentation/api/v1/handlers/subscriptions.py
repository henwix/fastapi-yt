from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Request, status
from pydantic import HttpUrl

from app.application.common.pagination import CursorPagination
from app.application.subscriptions.commands import SubscribeCommand, UnsubscribeCommand
from app.application.subscriptions.queries import (
    GetSubscribersQuery,
    GetSubscriptionsQuery,
    SubscriptionsSorting,
)
from app.application.subscriptions.usecases import (
    GetSubscribersUseCase,
    GetSubscriptionsUseCase,
    SubscribeUseCase,
    UnsubscribeUseCase,
)
from app.domain.auth.exceptions import JWTTokenExpiredError, JWTTokenInvalidError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError, ChannelNotFoundBySlugError
from app.domain.common.exceptions.pagination import InvalidCursorError
from app.domain.subscriptions.exceptions import (
    SelfSubscriptionError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di import CurrentChannelID
from app.presentation.api.v1.handlers.common.path_params import PathChannelSlug
from app.presentation.api.v1.handlers.common.query_params import CursorPaginationParams
from app.presentation.api.v1.schemas.requests.subscriptions import SubscriptionsSortingParamsSchema
from app.presentation.api.v1.schemas.responses.common import CursorPaginationResponse
from app.presentation.api.v1.schemas.responses.subscriptions import DetailedSubscriptionOutSchema, SubscriptionOutSchema

router = APIRouter(
    prefix='/channels',
    tags=['Subscriptions'],
    route_class=DishkaRoute,
)


@router.post(
    path='/{channel_slug}/subscriptions',
    status_code=status.HTTP_201_CREATED,
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
            ChannelNotFoundBySlugError,
        ),
        status.HTTP_409_CONFLICT: error_response(
            SubscriptionAlreadyExistsError,
            SelfSubscriptionError,
        ),
    },
)
async def subscribe(
    channel_slug: PathChannelSlug,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[SubscribeUseCase],
) -> SubscriptionOutSchema:
    command = SubscribeCommand(current_channel_id=current_channel_id, channel_slug=channel_slug)
    subscription = await use_case.execute(command=command)
    return SubscriptionOutSchema.from_entity(entity=subscription)


@router.delete(
    path='/{channel_slug}/subscriptions',
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
            ChannelNotFoundBySlugError,
            SubscriptionNotFoundError,
        ),
    },
)
async def unsubscribe(
    channel_slug: PathChannelSlug,
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[UnsubscribeUseCase],
) -> None:
    command = UnsubscribeCommand(current_channel_id=current_channel_id, channel_slug=channel_slug)
    await use_case.execute(command=command)


@router.get(
    path='/subscribers',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            InvalidCursorError,
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
    },
)
async def get_subscribers(
    current_channel_id: CurrentChannelID,
    sorting: Annotated[SubscriptionsSortingParamsSchema, Depends()],
    pagination: CursorPaginationParams,
    use_case: FromDishka[GetSubscribersUseCase],
    request: Request,
) -> CursorPaginationResponse[DetailedSubscriptionOutSchema]:
    query = GetSubscribersQuery(
        current_channel_id=current_channel_id,
        sorting=SubscriptionsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    subscribers, cursor = await use_case.execute(query=query)
    return CursorPaginationResponse(
        next_page=HttpUrl(str(request.url.include_query_params(cursor=cursor))) if cursor else None,
        results=[DetailedSubscriptionOutSchema.from_dto(dto=sub) for sub in subscribers],
    )


@router.get(
    '/subscriptions',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(
            InvalidCursorError,
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
    },
)
async def get_subscriptions(
    current_channel_id: CurrentChannelID,
    sorting: Annotated[SubscriptionsSortingParamsSchema, Depends()],
    pagination: CursorPaginationParams,
    use_case: FromDishka[GetSubscriptionsUseCase],
    request: Request,
) -> CursorPaginationResponse[DetailedSubscriptionOutSchema]:
    query = GetSubscriptionsQuery(
        current_channel_id=current_channel_id,
        sorting=SubscriptionsSorting(**sorting.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    subscriptions, cursor = await use_case.execute(query=query)
    return CursorPaginationResponse(
        next_page=HttpUrl(str(request.url.include_query_params(cursor=cursor))) if cursor else None,
        results=[DetailedSubscriptionOutSchema.from_dto(dto=sub) for sub in subscriptions],
    )
