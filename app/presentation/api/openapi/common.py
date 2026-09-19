from pydantic import BaseModel

from app.domain.common.exceptions.base import AppError
from app.presentation.api.v1.schemas.base import DetailSchema


def error_response(*errors: type[AppError]) -> dict[str, type[BaseModel] | dict]:
    examples = {
        error.__name__: {'summary': f'{error.__name__}', 'value': {'detail': error.message}} for error in errors
    }
    return {
        'model': DetailSchema,
        'content': {
            'application/json': {
                'examples': examples,
            },
        },
    }
