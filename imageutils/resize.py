from PIL.ExifTags import TAGS
from io import BytesIO
import base64
from PIL import Image, ImageOps
import uuid
import os
try:
    from .image_saver import save as save_image
except ImportError:
    from image_saver import save as save_image
import logging

logger = logging.getLogger(__name__)


class ImageShrinker:
    """Handles image resizing to meet target file sizes, with optional base64 encoding size checks"""

    def __init__(self, quality: int = 85):
        self.quality = quality

    def _get_file_size(self, img: Image.Image) -> int:
        """Get file size in bytes of a PIL Image"""
        img_byte_arr = BytesIO()
        save_image(img, img_byte_arr, quality=self.quality)
        return img_byte_arr.tell()

    def _get_base64_size(self, img: Image.Image) -> int:
        """Get size in bytes of base64 encoded image"""
        img_byte_arr = BytesIO()
        save_image(img, img_byte_arr, quality=self.quality)
        base64_str = base64.b64encode(img_byte_arr.getvalue())
        return len(base64_str)

    def _resize_to_dimensions(self, img: Image.Image, ratio: float) -> Image.Image:
        """Resize image by a ratio while maintaining aspect ratio"""
        before_orientation = get_exif_orientation(img)
        logger.debug(f"Before transposing: Orientation = {before_orientation}")
        img = ImageOps.exif_transpose(img)
        after_orientation = get_exif_orientation(img)
        logger.debug(f"After transposing: Orientation = {after_orientation}")
        new_width = int(img.width * ratio)
        new_height = int(img.height * ratio)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def resize_to_filesize(self, img: Image.Image, target_size_mb: float) -> Image.Image:
        """
        Resize image to meet target file size in megabytes

        Args:
            img: PIL Image to resize
            target_size_mb: Target file size in megabytes

        Returns:
            Resized PIL Image
        """
        target_size_bytes = int(target_size_mb * 1024 * 1024)
        current_size = self._get_file_size(img)
        ratio = 1.0
        resized = img
        logger.debug(
            f"Initial size: {current_size}, Target: {target_size_bytes}, Ratio: {ratio}")

        while current_size > target_size_bytes and ratio > 0.1:
            ratio *= (target_size_bytes / current_size) ** 0.5
            resized = self._resize_to_dimensions(img, ratio)
            current_size = self._get_file_size(resized)
            logger.debug(
                f"New size: {current_size}, Target: {target_size_bytes}, Ratio: {ratio}")
        # Save the resized image to a temp file for debugging if needed
        if logger.isEnabledFor(logging.DEBUG):
            os.makedirs("temp", exist_ok=True)
            temp_filename = f"temp/{uuid.uuid4()}.jpg"
            save_image(resized, temp_filename, quality=self.quality)
            logger.debug(f"Saved debug image to {temp_filename}")
        return resized

    def resize_to_base64_size(self, img: Image.Image, target_size_mb: float) -> Image.Image:
        """
        Resize image to meet target base64 encoded size in megabytes

        Args:
            img: PIL Image to resize
            target_size_mb: Target base64 encoded size in megabytes

        Returns:
            Resized PIL Image
        """
        target_size_bytes = int(target_size_mb * 1024 * 1024)
        current_size = self._get_base64_size(img)
        ratio = 1.0
        resized = img
        logger.debug(
            f"Initial size: {current_size}, Target: {target_size_bytes}, Ratio: {ratio}")

        while current_size > target_size_bytes and ratio > 0.1:
            ratio *= (target_size_bytes / current_size) ** 0.5
            resized = self._resize_to_dimensions(img, ratio)
            current_size = self._get_base64_size(resized)
            logger.debug(
                f"New size: {current_size}, Target: {target_size_bytes}, Ratio: {ratio}")

        # Save the resized image to a temp file for debugging if needed
        if logger.isEnabledFor(logging.DEBUG):
            os.makedirs("temp", exist_ok=True)
            temp_filename = f"temp/{uuid.uuid4()}.jpg"
            save_image(resized, temp_filename, quality=self.quality)
            logger.debug(f"Saved debug image to {temp_filename}")

        return resized


def get_exif_orientation(img):
    exif = img.getexif()
    if exif:
        for tag, value in exif.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == "Orientation":
                return value
    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s - %(levelname)s - %(message)s')
    logger.info("Starting the image resizing script")
    fp = r"C:\Users\driem\quack\A person holding a  Do Not Touch  sign near construction equipment..jpg"
    logger.info(F"raw size: {len(open(fp, 'rb').read())}")
    logging.getLogger('PIL.TiffImagePlugin').setLevel(logging.WARNING)
    img = Image.open(fp)
    print("image format:", img.format)
    # exit()
    resizer = ImageShrinker(120)
    img = resizer.resize_to_filesize(img, 5)
