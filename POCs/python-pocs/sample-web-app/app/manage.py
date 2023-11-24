import os

import aiohttp_jinja2
import jinja2
from aiohttp import web

from app.common.utils import load_config, get_logger
from app.config import CONFIG


def create_app():
    app = web.Application(client_max_size=1024 * 1024 * 5)
    config_name = os.getenv('ENVIRONMENT', 'development')
    jinja2_env = aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('app/templates/'))
    app.config = load_config(CONFIG[config_name])
    logger = get_logger()
    logger.info(f'Starting server for: [{app.config.ENVIRONMENT}]')
    return app, logger
