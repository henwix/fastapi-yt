from typing import Annotated
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.common.interfaces.jwt import IJWTService

bearer_schema = HTTPBearer()


@inject
async def get_current_channel_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_schema)],
    jwt_service: FromDishka[IJWTService],
) -> UUID:
    token = credentials.credentials
    token_payload = jwt_service.decode_access_token(token=token)
    return token_payload['sub']


CurrentChannelID = Annotated[UUID, Depends(get_current_channel_id)]
