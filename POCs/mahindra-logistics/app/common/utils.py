import logging
import os
import sys
import traceback
from configparser import ConfigParser
from io import StringIO
from logging.handlers import TimedRotatingFileHandler
from threading import Thread
from flask import request
from datetime import datetime
from flask import current_app
import inspect
import requests
import cgi

from app.business_rule_exception import FailedToDownloadFileFromURLException, InvalidFileException


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


def stop_watch(f):
    def timer(*args, **kwargs):
        start = datetime.now()
        x = f(*args, **kwargs)
        end = datetime.now()
        diff = end - start
        try:
            is_method = inspect.getfullargspec(f)[0][0] == 'self'
        except Exception as e:
            current_app.logger.info(e)
            is_method = False

        if is_method:
            name = '{}.{}'.format(args[0].__class__.__name__, f.__name__)
        else:
            name = '{}.{}'.format(f.__module__, f.__name__)

        current_app.logger.info(f'StopWatch => [{name}] Took: [{diff}]')
        return x

    return timer


@stop_watch
def file_downloader(url, target):
    try:
        current_app.logger.info(f"Downloading URL from: {url}")
        r = requests.get(url, allow_redirects=True)
        current_app.logger.info(f"Response: {r.status_code}")
        current_app.logger.info(f"Response Header: {r.headers}")
        if r.status_code == 200:
            file = url.split('/')[-1]
            content_disposition = r.headers.get('Content-Disposition')
            content_type = r.headers.get('Content-Type')
            if file and file.split('.')[-1] in current_app.config['ALLOWED_EXT']:
                filename = file
            elif content_disposition:
                value, params = cgi.parse_header(content_disposition)
                filename = params['filename']
            elif content_type:
                filename = file + '.' + content_type.split('/')[-1]
            else:
                raise InvalidFileException(url)
            file_path = os.path.join(target, filename)
            with open(file_path, 'wb') as f:
                f.write(r.content)
            current_app.logger.info(f"File saved at: {file_path}")
            return file_path, filename
        else:
            raise FailedToDownloadFileFromURLException(url)
    except FailedToDownloadFileFromURLException:
        raise
    except Exception as e:
        current_app.logger.error('%s -> %s', e, traceback.format_exc())
        raise FailedToDownloadFileFromURLException(url)
