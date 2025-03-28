import base64
from typing import IO

import pytest
from pydantic_ai import capture_run_messages, models
from pydantic_ai.messages import (ModelRequest, ModelResponse,
                                  SystemPromptPart, TextPart, ToolCallPart,
                                  ToolReturnPart, UserPromptPart)
from pydantic_ai.models.test import TestModel

from .context import Context, Entity
from .descriptions import Description
from .pydantic_ai_agent import ImageDescriber

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


async def test_describe_image(image_describer: ImageDescriber, red_square_file: IO):
    with capture_run_messages() as messages:
        result = await image_describer.describe_image(red_square_file)
        print(messages)
    assert result.title
