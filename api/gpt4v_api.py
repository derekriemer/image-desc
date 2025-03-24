import logging
import re

from openai import AsyncOpenAI

from imageutils.convert import encode_image

from .base_api import BaseAPI
from .exceptions import AiProcessingException
from .descriptions import Description
from .system_prompt import description_system_prompt

logger = logging.getLogger(__name__)  # Use the existing logger


class GPT4VAPI(BaseAPI):
    """pylint is stupid."""

    def __init__(self):
        self.api_sdk = AsyncOpenAI()
        self.context = Context()

    def append_context(self, context: Context):
        self.context = context

   async def generate_description(self, image_file):
        base64_image = encode_image(image_file)
        response = await self.api_sdk.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": description_system_prompt},
                {"role": "user", "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    }],
                 }
            ],
            max_tokens=400
        )
        description = response.choices[0].message.content
        if not description:
            logging.warning("The file %s cannot be processed. Refusal Reason: %s",
                            image_file, response.choices[0].message.refusal)
            raise AiProcessingException
        logging.info(description)
        fields = [i.strip() for i in re.split(r"-{20,}", description)]
        short_desc = fields[0] if fields else "Untitled"
        long_desc = "\n".join(fields[2:]).strip() if len(
            fields) > 2 else "No description available"
        entities = fields[1].strip() if len(
            fields) > 1 else "Uncategorized"
        return Description(short_desc, entities, long_desc)

    def generate_entities(self, image_path):
        # Placeholder for future implementation
        raise NotImplementedError("This method is not implemented yet.")
