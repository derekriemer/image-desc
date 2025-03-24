from fsspec.spec import AbstractFileSystem
from abc import ABC, abstractmethod

class FileGetter(ABC):
    @abstractmethod
    def get_file(self)-> File: