from polyfactory.factories import DataclassFactory

from app.application.posts.commands import CreatePostCommentCommand, DeletePostCommentCommand


class CreatePostCommentCommandFactory(DataclassFactory[CreatePostCommentCommand]):
    __model__ = CreatePostCommentCommand


class DeletePostCommentCommandFactory(DataclassFactory[DeletePostCommentCommand]):
    __model__ = DeletePostCommentCommand
