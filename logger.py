import logging
import asyncio
import sys
import os

file_lock = asyncio.Lock()

def setup_logging():
    log_filename = 'image_describer.log'
    OLD_LOG_FILE_NAME = 'image_describer-old.log'
    if os.path.exists(log_filename):
        if os.path.exists(OLD_LOG_FILE_NAME):
            os.remove(OLD_LOG_FILE_NAME)
        os.rename(log_filename, OLD_LOG_FILE_NAME)
    logging.basicConfig(filename=log_filename, level=logging.INFO,
        format='%(asctime)s - %(module)s - %(levelname)s - %(message)s', filemode="w")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception"   , exc_info=(exc_type, exc_value, exc_traceback))
sys.excepthook = handle_exception


async def log_progress(progress):
    async with file_lock:
        logging.info("Processed %d images", progress)
