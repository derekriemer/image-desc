import logging
from functools import reduce
from io import BytesIO
from typing import IO

import fsspec
from configobj import ConfigObj
from PIL import Image
from pydantic_ai import Agent, BinaryContent, RunContext, models

from imageutils.resize import ImageShrinker
from imageutils.image_saver import save as save_image

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
    def get_agent(cls, conf) -> Agent:
        agent = Agent(
            model=conf['model'],
            deps_type=Context,
            model_settings={'temperature': 0.0, }
        )

        @agent.system_prompt
        def system_prompt(ctx: RunContext[Context]) -> str:
            return description_system_prompt.replace("{{CONTEXT}}", ctx.deps.model_dump_json())

        return agent

    def __init__(self, deps: Context, conf: ConfigObj):
        self.conf = conf
        self.deps = deps
        self.agent = ImageDescriber.get_agent(conf)

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

    def _merge_config_sections(self, subconfigs):
        """ Merges a list of subconfigs together, such that keys in more specific subconfigs override keys in less specific subconfigs.

        Constraint: subconfigs: [0...n] where 0  less specific than 1 ... n"""
        match len(subconfigs):
            case 0:
                return {}
            case 1:
                return subconfigs[0]
            case _:
                return reduce(lambda merged, next: merged.update(next), subconfigs)

    def _get_provider_config(self):
        """ Retrieves the provider-specific configuration based on the model name. Merges less specific provider configs with more specific provider configs, such that configs for a specific model can be provided. This assumes that the - separator is used to override model settings for progressively deeper classes of model."""
        model = self.conf.get('model')
        if not model:
            return
        model_parts = model.split("-")
        subconfigs = []
        # model[:1] retreives up to but not including 1, thus we offset the
        # range by 1 such that 0...n-1 becomes 1...n
        for index in range(1, len(model_parts)+1):
            model_prefix = "-".join(model_parts[:index])
            subconfig = self.conf.get(model_prefix)
            if subconfig:
                subconfigs.append(subconfig)
        return self._merge_config_sections(subconfigs)

    def _resize_if_needed(self, image_bytes: bytes) -> bytes:
        """
        Resizes the image if needed based on model configuration.
        """
        provider_config = self._get_provider_config()
        if not provider_config:
            return image_bytes

        # Check if resize is needed
        resize_to = provider_config.get('resize_to')
        if not resize_to:
            return image_bytes

        # Convert target size to float (MB)
        try:
            target_size_mb = float(resize_to)
        except (TypeError, ValueError):
            logger.warning("Invalid resize_to value in config: %s", resize_to)
            return image_bytes

        # Initialize shrinker and load image
        shrinker = ImageShrinker()
        img = Image.open(BytesIO(image_bytes))

        # Resize based on encoding type
        use_base64 = provider_config.get('b64', False)
        if use_base64:
            resized_img = shrinker.resize_to_base64_size(img, target_size_mb)
        else:
            resized_img = shrinker.resize_to_filesize(img, target_size_mb)

        output = BytesIO()
        save_image(resized_img, output, quality=shrinker.quality)
        result_bytes = output.getvalue()
        result_size_mb = len(result_bytes) / (1024 * 1024)
        logger.debug(f"Resized image size: {result_size_mb:.2f}MB")

        return result_bytes

    async def describe_image(self, image_path: str) -> Description:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            image_bytes = self._resize_if_needed(image_bytes)

        response = await self.agent.run(
            [BinaryContent(
                image_bytes, media_type=self._get_mime_type(image_bytes))],
            result_type=Description,
            deps=self.deps)
        description = response.data
        if not description:
            raise AiProcessingException("No description generated.")
        return description
