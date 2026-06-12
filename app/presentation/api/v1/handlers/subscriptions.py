from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, Depends, Path, Request, status

from app.application.commands.subscriptions import SubscribeCommand, UnsubscribeCommand
from app.application.common.pagination import CursorPagination
from app.application.queries.subscriptions import GetSubscribersQuery, GetSubscribersSortOrder
from app.application.use_cases.subscriptions.get_subscribers import GetSubscribersUseCase
from app.application.use_cases.subscriptions.subscribe import SubscribeUseCase
from app.application.use_cases.subscriptions.unsubscribe import UnsubscribeUseCase
from app.domain.auth.exceptions import JWTExpiredTokenError, JWTInvalidTokenError, NotAuthenticatedError
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundBySlugError, ChannelNotFoundError
from app.domain.common.constants import SLUG_PATTERN
from app.domain.subscriptions.exceptions import SubscriptionAlreadyExistsError, SubscriptionNotFoundError
from app.presentation.api.openapi.common import error_response
from app.presentation.api.v1.di.current_channel_id import CurrentChannelID
from app.presentation.api.v1.schemas.base import CursorPaginationParams
from app.presentation.api.v1.schemas.subscriptions import (
    SubscriptionCursorResponse,
    SubscriptionSchema,
    SubscriptionSortParams,
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
        status.HTTP_404_NOT_FOUND: error_response(ChannelNotFoundError, ChannelNotFoundBySlugError),
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
            ChannelNotFoundError,
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
        status.HTTP_401_UNAUTHORIZED: error_response(
            NotAuthenticatedError,
            JWTExpiredTokenError,
            JWTInvalidTokenError,
        ),
        status.HTTP_403_FORBIDDEN: error_response(ChannelNotActiveError),
        status.HTTP_404_NOT_FOUND: error_response(
            ChannelNotFoundError,
        ),
    },
)
async def get_subscribers(
    current_channel_id: CurrentChannelID,
    use_case: FromDishka[GetSubscribersUseCase],
    sort: Annotated[SubscriptionSortParams, Depends()],
    pagination: Annotated[CursorPaginationParams, Depends()],
    request: Request,
) -> SubscriptionCursorResponse:
    query = GetSubscribersQuery(
        current_channel_id=current_channel_id,
        sorting=GetSubscribersSortOrder(**sort.model_dump()),
        pagination=CursorPagination(**pagination.model_dump(exclude_none=True)),
    )
    subscribers = await use_case.execute(query=query)
    return SubscriptionCursorResponse(
        next_page=str(request.url.include_query_params(cursor=str(subscribers[-1].id))) if subscribers else None,
        results=[SubscriptionSchema.from_entity(entity=sub) for sub in subscribers],
    )


# @router.get(path='/subscriptions')
# async def get_subscriptions(): ...
