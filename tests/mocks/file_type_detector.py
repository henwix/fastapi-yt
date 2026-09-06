from app.application.common.interfaces.file_type_detector import IFileTypeDetector


class MockFileTypeDetector(IFileTypeDetector):
    def __init__(self) -> None:
        super().__init__()
        self.FILE_TYPE: str = 'image/png'

    def detect(self, content: bytes) -> str:
        return self.FILE_TYPE
