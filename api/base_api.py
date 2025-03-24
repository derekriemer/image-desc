from abc import ABC, abstractmethod
from typing import IO
from .descriptions import Description, Entities


class AIAPI(ABC):
    """
    Abstract base class for AI APIs
    This class defines the interface for any AI API that generates descriptions and entities from images.
    """

    def __init__(self):
        self.context = None

    @abstractmethod
    def add_context(self, context):
        """Add context to the AI API instance."""
        self.context = context

    @abstractmethod
    async def generate_description(self, image_file: IO) -> Description:
        """Generate a description from the given image file."""
        ...

    @abstractmethod
    async def generate_entities(self, image_file: IO) -> Entities:
        """Generate entities from the given image file."""
        ...
