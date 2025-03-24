import asyncio
import os

from aiofiles import open as aio_open

file_lock = asyncio.Lock()

RESULTS_FILE = 'results.csv'

async def init_results():
    """Initialize the results file by opening it in write mode to reset it."""
    async with file_lock:
        async with aio_open(RESULTS_FILE, 'w') as csvfile:
            await csvfile.write('"file name","short description","categories","detailed description"\n')

async def save_results(results):
    """pylint, die"""
    async with file_lock:
        async with aio_open(RESULTS_FILE, 'a', newline='') as csvfile:
            for result in filter(None, results):
                await csvfile.write(
                    ",".join([f'"{r.replace('"', '""')}"' for r in result]) + "\n")

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
