import pytest
from pydantic_ai import models

from api.exceptions import AiProcessingException
from image_processor import process_image, process_images

pytestmark = pytest.mark.anyio
models.ALLOW_MODEL_REQUESTS = False


async def test_process_image__processes_a_valid_image(image_describer, red_square_file):
    result = await process_image(red_square_file, image_describer)


async def test_process_image__raises_exception_for_invalid_image(image_describer, mocker, red_square_file):
    mocker.patch.object(image_describer, 'describe_image',
                        side_effect=AiProcessingException)
    # Pass an invalid file path to simulate an error.
    result = await process_image(red_square_file, image_describer)
    assert result is None
