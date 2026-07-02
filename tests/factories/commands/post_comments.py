from polyfactory.factories import DataclassFactory

from app.application.post_comments.commands import CreatePostCommentCommand, DeletePostCommentCommand


class CreatePostCommentCommandFactory(DataclassFactory[CreatePostCommentCommand]):
    __model__ = CreatePostCommentCommand


class DeletePostCommentCommandFactory(DataclassFactory[DeletePostCommentCommand]):
    __model__ = DeletePostCommentCommand
