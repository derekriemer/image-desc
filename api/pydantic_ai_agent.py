import logging
from io import BytesIO
from typing import IO

import fsspec
from PIL import Image
from pydantic_ai import Agent, BinaryContent, RunContext
from pydantic_ai import models

from .context import Context
from .descriptions import Description
from .exceptions import AiProcessingException
from .system_prompt import description_system_prompt

logger = logging.getLogger(__name__)


class ImageDescriber:
    """
    Class to describe a batch of images.
    The describer creates an agent immediately upon creation that then is used to describe images.
    The agent has its context passed in via its dependency injection system.
    Each agent can b run against arbitrary agents, but for now, context cannot be updated.
    """

    @classmethod
    def get_agent(cls) -> Agent:
        agent = Agent(
            model=("gpt-4o-mini" if models.ALLOW_MODEL_REQUESTS else "test"),
            deps_type=Context,
        )

        @agent.system_prompt
        def system_prompt(ctx: RunContext[Context]) -> str:
            return description_system_prompt + "\n" + ctx.deps.model_dump_json()

        return agent

    def __init__(self, deps: Context):
        self.deps = deps
        self.agent = ImageDescriber.get_agent()

    def _get_mime_type(self, image_data: bytes) -> str:
        """ Gets a mimetype from a file using pillow. """
        try:
            image = Image.open(BytesIO(image_data))
            mime_type = image.get_format_mimetype()
            if mime_type:
                return mime_type
        except IOError as e:
            logger.exception(
                "Error processing mimetype for image file", exc_info=e)
            raise AiProcessingException() from e

    async def describe_image(self, image_path: str) -> Description:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()

        response = await self.agent.run(
            [BinaryContent(
                image_bytes, media_type=self._get_mime_type(image_bytes))],
            result_type=Description,
            deps=self.deps)
        description = response.data
        if not description:
            raise AiProcessingException("No description generated.")
        return description
