from faker import Faker
from polyfactory.factories import DataclassFactory

from app.application.videos.commands import (
    AbortVideoMultipartUploadCommand,
    CompleteVideoMultipartUploadCommand,
    CreateVideoMultipartUploadCommand,
    GenerateVideoDownloadUrlCommand,
    GenerateVideoPartUploadUrlCommand,
)


class CreateVideoMultipartUploadCommandFactory(DataclassFactory[CreateVideoMultipartUploadCommand]):
    __model__ = CreateVideoMultipartUploadCommand
    __faker__ = Faker()

    @classmethod
    def filename(cls) -> str:
        return 'test.mp4'

    @classmethod
    def title(cls) -> str:
        return cls.__faker__.text(max_nb_chars=100)


class GenerateVideoPartUploadUrlCommandFactory(DataclassFactory[GenerateVideoPartUploadUrlCommand]):
    __model__ = GenerateVideoPartUploadUrlCommand
    __faker__ = Faker()

    @classmethod
    def part_number(cls) -> int:
        return cls.__faker__.random_int(min=1, max=10000)


class CompleteVideoMultipartUploadCommandFactory(DataclassFactory[CompleteVideoMultipartUploadCommand]):
    __model__ = CompleteVideoMultipartUploadCommand


class AbortVideoMultipartUploadCommandFactory(DataclassFactory[AbortVideoMultipartUploadCommand]):
    __model__ = AbortVideoMultipartUploadCommand


class GenerateVideoDownloadUrlCommandFactory(DataclassFactory[GenerateVideoDownloadUrlCommand]):
    __model__ = GenerateVideoDownloadUrlCommand
