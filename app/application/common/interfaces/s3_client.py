from abc import ABC, abstractmethod


class IS3Client(ABC):
    @abstractmethod
    def client(self): ...
