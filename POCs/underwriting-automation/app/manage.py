import os

from aiohttp import web
from app.constant import CLIENT_MAX_SIZE
from app.common.utils import load_config, get_logger
from app.config import CONFIG


def create_app():
    app = web.Application(client_max_size=CLIENT_MAX_SIZE)
    config_name = os.getenv('ENVIRONMENT', 'development')
    app.config = load_config(CONFIG[config_name])
    logger = get_logger()
    print(f'Starting server for: [{app.config.ENVIRONMENT}]')
    return app, logger
