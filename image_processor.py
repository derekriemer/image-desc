import os
import re
import asyncio
import logging

from data_persistence import save_results
from logger import log_progress
from api.exceptions import AiProcessingException

file_lock = asyncio.Lock()

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')


async def process_image(image_path, api, short_description_length):
    try:
        short_description, detailed_description, categories = await api.generate_description(
            image_path)
    except AiProcessingException:
        return

    short_description = ' '.join(short_description.split()[
        :short_description_length])
    short_description = re.sub(r"[^a-zA-Z0-9._-]", " ", short_description)

    new_image_path = ""

    async with file_lock:
        num = 0
        while True:
            try:
                new_image_path = os.path.join(os.path.dirname(image_path),
                                              f"{short_description}{'-'+str(num) if num else ''}.jpg")
                os.rename(image_path, new_image_path)
                break
            except FileExistsError:
                num += 1
    return new_image_path, short_description, detailed_description, categories


async def process_images(image_folder,
                         api,
                         short_description_length,
                         progress,
                         batch_size=5):
    image_paths = []
    for root, _, files in os.walk(image_folder):
        for file in files:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_paths.append(os.path.join(root, file))
    if progress:
        image_paths = image_paths[progress:]

    for i in range(0, len(image_paths), batch_size):
        batch = image_paths[i:i + batch_size]
        for image_path in batch:
            try:
                result = await process_image(image_path, api, short_description_length)
                if result:
                    await save_results([result])
                await log_progress(i + batch.index(image_path) + 1)
            except Exception as e:
                logging.exception("exception processing image %s. Exception: %s", image_path, e)

            # Delay a few seconds to avoid rate limiting.
        await asyncio.sleep(5)
