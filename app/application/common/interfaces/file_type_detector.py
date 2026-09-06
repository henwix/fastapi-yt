from abc import ABC, abstractmethod


class IFileTypeDetector(ABC):
    @abstractmethod
    def detect(self, content: bytes) -> str: ...
