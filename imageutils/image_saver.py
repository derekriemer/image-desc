from PIL import Image
import logging

logger = logging.getLogger(__name__)


def save(img: Image.Image, output_path: str, quality=85) -> None:
    """
    Save image while preserving EXIF metadata

    Args:
        img: PIL Image to save
        output_path: Path where to save the image
    """
    try:
        if "exif" in img.info:
            img.save(output_path, format="JPEG",
                     quality=quality, exif=img.info["exif"])
        else:
            img.save(output_path, format="JPEG", quality=quality)
    except Exception as e:
        # Log error but don't crash if saving with EXIF fails
        logger.error(f"Error saving image with EXIF data: {e}")
        # Fallback to saving without EXIF
        img.save(output_path, format="JPEG", quality=quality)
