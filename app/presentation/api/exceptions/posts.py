from fastapi import status

from app.domain.common.exceptions.base import AppError
from app.domain.posts.exceptions import (
    PostAccessForbiddenError,
    PostCommentAccessForbiddenError,
    PostCommentNotFoundError,
    PostCommentReactionNotFoundError,
    PostNotFoundError,
    PostReactionNotFoundError,
)


def init_posts() -> dict[type[AppError], int]:
    return {
        # Posts
        PostAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post reactions
        PostReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post comments
        PostCommentAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostCommentNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post comment reactions
        PostCommentReactionNotFoundError: status.HTTP_404_NOT_FOUND,
    }
