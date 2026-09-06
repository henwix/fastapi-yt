import magic

from app.application.common.interfaces.file_type_detector import IFileTypeDetector


class FileTypeDetector(IFileTypeDetector):
    def detect(self, content: bytes) -> str:
        return magic.from_buffer(content, mime=True)
