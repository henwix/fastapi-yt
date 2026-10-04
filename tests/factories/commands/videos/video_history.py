from polyfactory.factories import DataclassFactory

from app.application.videos.commands import (
    AddVideoToHistoryCommand,
    ClearVideoHistoryCommand,
    DeleteVideoFromHistoryCommand,
)


class AddVideoToHistoryCommandFactory(DataclassFactory[AddVideoToHistoryCommand]):
    __model__ = AddVideoToHistoryCommand


class DeleteVideoFromHistoryCommandFactory(DataclassFactory[DeleteVideoFromHistoryCommand]):
    __model__ = DeleteVideoFromHistoryCommand


class ClearVideoHistoryCommandFactory(DataclassFactory[ClearVideoHistoryCommand]):
    __model__ = ClearVideoHistoryCommand
