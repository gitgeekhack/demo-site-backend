import logging
import os
from flask import Flask
from app.common.utils import setup_logger, read_properties_file
from app.config import CONFIG


def create_app(debug=False):
    app = Flask(__name__, template_folder="./templates", static_folder="./static")
    app.debug = debug
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    config = read_properties_file(os.path.join(parent_dir, "environment.properties"))
    config_name = os.getenv('FLASK_CONFIGURATION', config['environment'])
    app.config.from_object(CONFIG[config_name])
    logger = setup_logger()
    app.logger.info('Starting [{}] server'.format(app.config['ENVIRONMENT']))
    return app, logger
