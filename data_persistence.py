import asyncio
import logging
import os
from typing import List

from aiofiles import open as aio_open

from api.descriptions import Description

file_lock = asyncio.Lock()

RESULTS_FILE = 'results.csv'

logger = logging.getLogger(__name__)


async def init_results():
    """Initialize the results file by opening it in write mode to reset it."""
    async with file_lock:
        async with aio_open(RESULTS_FILE, 'w') as csvfile:
            await csvfile.write('"file name","short description","people", "detailed description"\n')


def sanatize(value):
    return value.replace('"', '""')


def getEntities(entities):
    print(entities)
    return "\n".join([f"{p.name}, {float(p.confidence)*100}%" for p in entities])


async def save_results(fn: str, results: List[Description]):
    """pylint, die"""
    fn = "\\".join(fn.split('/')[-2:])
    async with file_lock:
        async with aio_open(RESULTS_FILE, 'a', newline='') as csvfile:
            for result in filter(None, results):
                logger.info(f"Saving result: {result}")
                await csvfile.write(
                    F'"{sanatize(fn)}","{sanatize(result.title)}","{sanatize(getEntities(result.entities))}","{sanatize(result.long_description)}"\n')


def load_progress():
    """pylint, die"""
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r', encoding='utf-8') as f:
            return int(f.read().strip())
    return 0


def save_progress(progress):
    """pylint, die"""
    with open('progress.txt', 'w', encoding='utf-8') as f:
        f.write(str(progress))
