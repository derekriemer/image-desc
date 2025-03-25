import logging
from typing import IO


from PIL import Image
from pydantic_ai import Agent, BinaryContent, RunContext

from .context import Context
from .descriptions import Description
from .exceptions import AiProcessingException
from .system_prompt import description_system_prompt

logger = logging.getLogger(__name__)


def get_agent() -> Agent:
    agent = Agent(
        model="gpt-4o-mini",
        deps_type=Context,
    )

    @agent.system_prompt
    def system_prompt(ctx: RunContext[Context]) -> str:
        return description_system_prompt + "\n" + ctx.deps.model_dump_json()

    return agent


class ImageDescriber:
    """
    Class to describe a batch of images.
    The describer creates an agent immediately upon creation that then is used to describe images.
    The agent has its context passed in via its dependency injection system.
    Each agent can b run against arbitrary agents, but for now, context cannot be updated.
    """

    def __init__(self, deps: Context):
        self.deps = deps
        self.agent = get_agent()

    def _getMimeType(self, image_file: IO) -> str:
        """ Gets a mimetype from a file using pillow. """
        try:
            image = Image.open(image_file)
            mime_type = image.get_format_mimetype()
            if mime_type:
                return mime_type
        except IOError as e:
            logger.exception(
                "Error processing mimetype for image file", exc_info=e)
            raise AiProcessingException() from e

    async def describe_image(self, image_file) -> Description:
        response = await self.agent.run(
            BinaryContent(
                image_file, media_type=self._getMimeType(image_file)),
            result_type=Description,
        )
        description = response.data
        if not description:
            raise AiProcessingException("No description generated.")
        return description
