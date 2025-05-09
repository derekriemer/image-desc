import asyncio
import logging
import pathlib

import fsspec
from configobj import ConfigObj

from api.context import Context
from api.exceptions import AiProcessingException
from api.pydantic_ai_agent import ImageDescriber
from data_persistence import save_results
from log import log_progress

file_lock = asyncio.Lock()

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')


async def process_image(image_path: str, imageDescriber: ImageDescriber):
    try:
        return await imageDescriber.describe_image(
            image_path)
    except AiProcessingException as e:
        return
    except OSError as e:
        logger.exception(e)
        return


async def process_images(
        fs: fsspec.AbstractFileSystem,
        path: str,
        context: Context,
        conf: ConfigObj,
        progress):
    image_paths = []
    imageDescriber = ImageDescriber(context, conf)
    for root, _, files in fs.walk(path):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_paths.append(str(pathlib.Path(root) / file))
    if progress:
        image_paths = image_paths[progress:]
    batch_size = int(conf.get('batch_size', 5))
    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i + batch_size]
        for image_path in batch:
            try:
                result = await process_image(image_path, imageDescriber)
                if result:
                    await save_results(image_path, [result])
                    await log_progress(i + batch.index(image_path) + 1)
            except Exception as e:
                logging.exception(
                    "exception processing image %s. Exception: %s", image_path, e)
    # Delay a few seconds to avoid rate limiting.
    await asyncio.sleep(5)
