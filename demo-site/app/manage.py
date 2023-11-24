import os

import aiohttp_jinja2
import jinja2
from aiohttp import web

from app.common.utils import load_config, get_logger
from app.config import CONFIG


def create_app():
    app = web.Application(client_max_size=1024*1024*25)
    config_name = os.getenv('ENVIRONMENT', 'development')
    jinja2_env = aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('app/templates/'))
    app['static_root_url'] = '/static'
    app.router.add_static(app['static_root_url'], 'app/static/')
    app.config = load_config(CONFIG[config_name])
    logger = get_logger()
    print(f'Starting server for: [{app.config.ENVIRONMENT}]')
    return app, logger
