import os

from aiohttp import web

from app.common.utils import load_config, get_logger
from app.config import CONFIG


def create_app():
    app = web.Application()
    config_name = os.getenv('ENVIRONMENT', 'development')
    app.config = load_config(CONFIG[config_name])
    logger = get_logger()
    logger.info(f'Starting server for: [{app.config.ENVIRONMENT}]')
    return app, logger
