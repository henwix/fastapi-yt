from pydantic import BaseModel

from app.domain.common.exceptions import AppException


class DetailSchema(BaseModel):
    detail: str


def error_response(*errors: type[AppException]) -> dict:
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
