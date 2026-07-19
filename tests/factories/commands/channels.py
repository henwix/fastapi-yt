from random import Random

from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.channels.commands import (
    ConfirmChannelAvatarUploadCommand,
    CreateChannelCommand,
    DeleteChannelAvatarCommand,
    GenerateChannelAvatarUploadUrlCommand,
    SetChannelPasswordCommand,
    UpdateChannelCommand,
)
from app.domain.common.constants import Empty


class CreateChannelCommandFactory(DataclassFactory[CreateChannelCommand]):
    __model__ = CreateChannelCommand
    __faker__ = Faker()

    @classmethod
    def email(cls) -> str:
        return cls.__faker__.email()

    @classmethod
    def slug(cls) -> str:
        return cls.__faker__.slug()


class UpdateChannelCommandFactory(DataclassFactory[UpdateChannelCommand]):
    __model__ = UpdateChannelCommand
    __random__ = Random()
    __faker__ = Faker()

    @classmethod
    def slug(cls) -> str | Empty:
        return cls.__random__.choice([Empty.UNSET, cls.__faker__.slug()])


class SetChannelPasswordCommandFactory(DataclassFactory[SetChannelPasswordCommand]):
    __model__ = SetChannelPasswordCommand


class GenerateChannelAvatarUploadUrlCommandFactory(DataclassFactory[GenerateChannelAvatarUploadUrlCommand]):
    __model__ = GenerateChannelAvatarUploadUrlCommand


class ConfirmChannelAvatarUploadCommandFactory(DataclassFactory[ConfirmChannelAvatarUploadCommand]):
    __model__ = ConfirmChannelAvatarUploadCommand


class DeleteChannelAvatarCommandFactory(DataclassFactory[DeleteChannelAvatarCommand]):
    __model__ = DeleteChannelAvatarCommand
