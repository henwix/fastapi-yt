from polyfactory.factories import DataclassFactory

from app.application.posts.commands import CreatePostCommand, DeletePostCommand, UpdatePostCommand


class CreatePostCommandFactory(DataclassFactory[CreatePostCommand]):
    __model__ = CreatePostCommand


class DeletePostCommandFactory(DataclassFactory[DeletePostCommand]):
    __model__ = DeletePostCommand


class UpdatePostCommandFactory(DataclassFactory[UpdatePostCommand]):
    __model__ = UpdatePostCommand
