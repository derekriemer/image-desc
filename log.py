import logging
import asyncio
import sys
import os

file_lock = asyncio.Lock()


async def log_progress(progress):
    async with file_lock:
        logging.info("Processed %d images", progress)
