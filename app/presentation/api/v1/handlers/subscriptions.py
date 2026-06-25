from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Request, status

from app.application.common.pagination import CursorPagination
from app.application.subscriptions.commands import SubscribeCommand, UnsubscribeCommand
from app.application.subscriptions.queries import (
    GetSubscribersQuery,
    GetSubscriptionsQuery,
    SubscriptionsSorting,
)
from app.application.subscriptions.use_cases.get_subscribers import GetSubscribersUseCase
from app.application.subscriptions.use_cases.get_subscriptions import GetSubscriptionsUseCase
from app.application.subscriptions.use_cases.subscribe import SubscribeUseCase
from app.application.subscriptions.use_cases.unsubscribe import UnsubscribeUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError, ChannelNotFoundBySlugError
from app.domain.common.constants import SLUG_PATTERN
from app.domain.common.exceptions import InvalidCursorError
from app.domain.subscriptions.exceptions import SubscriptionAlreadyExistsError, SubscriptionNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.base import CursorPaginationParams
from app.presentation.api.v1.schemas.subscriptions import (
    DetailedSubscriptionSchema,
    SubscriptionSchema,
    SubscriptionsCursorResponse,
    SubscriptionsSortingParams,
)

router = APIRouter(
    prefix='/channels',
    tags=['Subscriptions'],
    route_class=DishkaRoute,
)


@router.post(
    path='/{channel_slug}/subscriptions',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(SubscriptionAlreadyExistsError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            ChannelNotFoundBySlugError,
        ),
    },
)
async def subscribe(
    channel_slug: Annotated[str, Path(min_length=1, max_length=40, pattern=SLUG_PATTERN)],
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[SubscribeUseCase],
) -> SubscriptionSchema:
    command = SubscribeCommand(current_channel_id=current_channel_id, channel_slug=channel_slug)
    subscription = await use_case.execute(command=command)
    return SubscriptionSchema.from_entity(entity=subscription)


@router.delete(
    path='/{channel_slug}/subscriptions',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
            ChannelNotFoundBySlugError,
            SubscriptionNotFoundError,
        ),
    },
)
async def unsubscribe(
    channel_slug: Annotated[str, Path(min_length=1, max_length=40, pattern=SLUG_PATTERN)],
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[UnsubscribeUseCase],
) -> None:
    command = UnsubscribeCommand(current_channel_id=current_channel_id, channel_slug=channel_slug)
    await use_case.execute(command=command)


@router.get(
    path='/subscribers',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(InvalidCursorError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def get_subscribers(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[GetSubscribersUseCase],
    sort: Annotated[SubscriptionsSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    request: Request,
) -> SubscriptionsCursorResponse:
    query = GetSubscribersQuery(
        current_channel_id=current_channel_id,
        sorting=SubscriptionsSorting(**sort.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    subscribers, cursor = await use_case.execute(query=query)
    return SubscriptionsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[DetailedSubscriptionSchema.from_dto(dto=sub) for sub in subscribers],
    )


@router.get(
    '/subscriptions',
    responses={
        status.HTTP_400_BAD_REQUEST: error_response(InvalidCursorError),
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundByIdError,
        ),
    },
)
async def get_subscriptions(
    current_channel_id: CurrentChannelID,
    sort: Annotated[SubscriptionsSortingParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    use_case: FromDishka[GetSubscriptionsUseCase],
    request: Request,
) -> SubscriptionsCursorResponse:
    query = GetSubscriptionsQuery(
        current_channel_id=current_channel_id,
        sorting=SubscriptionsSorting(**sort.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    subscriptions, cursor = await use_case.execute(query=query)
    return SubscriptionsCursorResponse(
        next_page=str(request.url.include_query_params(cursor=cursor)) if cursor else None,
        results=[DetailedSubscriptionSchema.from_dto(dto=sub) for sub in subscriptions],
    )
