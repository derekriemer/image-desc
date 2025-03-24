import argparse
import os
import asyncio
import pathlib

from configobj import ConfigObj
from dotenv import load_dotenv

from api.google_vision_api import GoogleVisionAPI
from api.gpt4v_api import GPT4VAPI
from data_persistence import load_progress, init_results
from image_processor import process_images
from logger import setup_logging


def parse_args():
    """duh"""
    parser = argparse.ArgumentParser(description="Image Describer CLI Tool")
    parser.add_argument('--image-folder',
                        help='Path to the image folder')
    parser.add_argument('--api', choices=[
                        'gpt-4', 'google-vision'], help='API to use for image description')
    parser.add_argument('--short-description-length', type=int,
                        default=15, help='Maximum number of words for short description')
    parser.add_argument('--config', default='config.ini',
                        help='Path to configuration file')
    parser.add_argument('--resume', action='store_true',
                        help='Resume from the last processed image')
    return parser.parse_args()


def load_config(config_path):
    return ConfigObj(config_path)


def merge_config_with_args(config, args):
    """
    Merges provided CLI arguments with the configuration.
    Arguments in CLI take precedence over config values.
    """
    if args.image_folder:
        config['image_folder'] = args.image_folder
    if args.api:
        config['ai_api'] = args.api
    if args.short_description_length:
        config['short_description_length'] = args.short_description_length
    if args.resume is not None:
        config['resume'] = args.resume

    return config


async def main():
    base_dir = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
    os.chdir((base_dir))
    setup_logging()
    # take environment variables from .env.
    load_dotenv(dotenv_path=base_dir / ".ENV", verbose=True)
    args = parse_args()
    config = load_config(args.config)
    config = merge_config_with_args(config, args)
    api = GPT4VAPI() if config['ai_api'] == 'openai' else GoogleVisionAPI()
    progress = load_progress() if config.get('resume', False) else None
    await init_results()
    await process_images(config['image_folder'], api,
                         config['short_description_length'], progress)

if __name__ == '__main__':
    asyncio.run(main())
