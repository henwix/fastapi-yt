from dataclasses import dataclass


@dataclass(kw_only=True, frozen=True)
class DeleteS3ObjectCommand:
    bucket: str
    key: str


@dataclass(kw_only=True, frozen=True)
class AbortMultipartUploadCommand:
    bucket: str
    key: str
    upload_id: str
