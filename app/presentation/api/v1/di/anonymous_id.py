from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Cookie, Depends, Response


def get_anonymous_id(
    response: Response,
    anonymous_id: Annotated[UUID | None, Cookie()] = None,
) -> UUID:
    if anonymous_id is None:
        anonymous_id = uuid4()
        response.set_cookie(
            key='anonymous_id',
            value=str(anonymous_id),
            max_age=60 * 60 * 24 * 365,  # 1 year
            httponly=True,
            secure=True,
        )

    return anonymous_id


AnonymousID = Annotated[UUID, Depends(get_anonymous_id)]
