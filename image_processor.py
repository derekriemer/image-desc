import asyncio
import logging
import os
from typing import IO

import fsspec

from api.context import Context
from api.pydantic_ai_agent import ImageDescriber
from api.exceptions import AiProcessingException
from data_persistence import save_results
from log import log_progress

file_lock = asyncio.Lock()

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
        progress,
        batch_size=5):
    image_paths = []
    imageDescriber = ImageDescriber(context)
    for root, _, files in fs.walk(path):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_paths.append(os.path.join(root, file))
    if progress:
        image_paths = image_paths[progress:]

    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i + batch_size]
        for image_path in batch:
            try:
                result = await process_image(image_path, imageDescriber)
                if result:
                    await save_results([result])
                    await log_progress(i + batch.index(image_path) + 1)
            except Exception as e:
                logging.exception(
                    "exception processing image %s. Exception: %s", image_path, e)
    # Delay a few seconds to avoid rate limiting.
    await asyncio.sleep(5)
