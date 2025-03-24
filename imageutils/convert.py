import base64
import io
import logging
from pathlib import Path
from typing import IO

from PIL import Image

logger = logging.getLogger(__name__)  # Use the existing logger


def encode_image(image_file: IO) -> str:
    """
    Converts an image (JPEG, PNG, TIFF, GIF, BMP) to a Base64-encoded string.
    TIFF and GIF will be converted to JPEG before encoding.

    Args:
        image_file(IO): File like image object.

    Returns:
        str: Base64-encoded image string or None if an error occurs.
    """
    if not image_file.is_file():
        logger.error("Image file not found: %s", image_file.name)
        return

    # Open image
    with Image.open(image_file) as img:
        img_format = img.format  # Store original format

        # Convert TIFF and GIF to JPEG (for AI model compatibility)
        if img_format in ["TIFF", "GIF"]:
            img = img.convert("RGB")
            img_format = "JPEG"
            logger.info("Converted %s from %s to JPEG.",
                        image_file.name, img.format)

    # Convert image to bytes
    buffered = io.BytesIO()
    img.save(buffered, format=img_format)

    # Encode to Base64
    return base64.b64encode(buffered.getvalue()).decode("utf-8")
    