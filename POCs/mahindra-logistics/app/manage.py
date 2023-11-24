import os

from flask import Flask

# noinspection PyUnresolvedReferences
from app.common.utils import start_logging
# noinspection PyUnresolvedReferences
from app.config import CONFIG

def create_app(debug=False):
    app = Flask(__name__, template_folder="./templates", static_folder="./static")
    app.debug = debug
    config_name = os.getenv('FLASK_CONFIGURATION', 'staging')
    app.config.from_object(CONFIG[config_name])
    start_logging(app)
    app.logger.info("App started")
    return app