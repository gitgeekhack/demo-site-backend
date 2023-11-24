import logging
import os
import sys
import traceback
from configparser import ConfigParser
from datetime import datetime
from io import StringIO
from logging.handlers import TimedRotatingFileHandler
from threading import Thread

from flask import current_app
from flask import request, logging as flask_logging


def timeit(f):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        x = f(*args, **kwargs)
        end = datetime.now()
        diff = end - start
        current_app.logger.info(f'Method [{f.__name__}] Took: [{diff}]')
        return x

    return wrapper


def async_execution(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()

    return wrapper


def make_dir(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def get_error_traceback(error):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    template = 'File: {file_name} : {file_line_no} \n Error: {err} \n Error Description: {err_info} \n ' \
               'Traceback: {traceback} \n API: {path}'
    text = template.format(file_name=exc_traceback.tb_frame.f_code.co_filename,
                           file_line_no=str(exc_traceback.tb_lineno),
                           err_info=error.__doc__,
                           err=str(error),
                           traceback=str(repr(traceback.format_tb(exc_traceback))),
                           path=request.path)
    return text


def read_properties_file(file_path):
    with open(file_path) as f:
        config = StringIO()
        config.write("[dummy_section]\n")
        config.write(f.read().replace("%", "%%"))
        config.seek(0, os.SEEK_SET)
        cp = ConfigParser()
        cp.read_file(config)
        return dict(cp.items("dummy_section"))


def start_logging(app):
    log_folder_location = os.path.abspath(os.path.join(__file__, '..', '..', 'logs'))
    make_dir(log_folder_location)
    app.logger.setLevel(logging.INFO)
    log_file = '{0}/log.txt'.format(log_folder_location)
    handler = TimedRotatingFileHandler(log_file, when='midnight', interval=1, delay=False, utc=False)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[Time: %(asctime)s] - '
        'Level: %(levelname)s - '
        '%(message)s - '
        'Module: %(module)s - '
        'Function: %(funcName)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)


def start_console_logger(app):
    formatter = logging.Formatter(
        '[Time: %(asctime)s] - '
        'Level: %(levelname)s - '
        'Module: %(module)s - '
        'Function: %(funcName)s - '
        '%(message)s')
    flask_logging.default_handler.setFormatter(formatter)
    app.logger.setLevel(logging.INFO)
