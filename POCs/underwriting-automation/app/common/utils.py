import os
import sys
import logging
from logging.handlers import RotatingFileHandler

from app.constant import AllowedFileType


def load_config(import_name):
    import_name = str(import_name).replace(":", ".")
    try:
        __import__(import_name)
    except ImportError:
        if "." not in import_name:
            raise
    else:
        return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit(".", 1)
    module = __import__(module_name, globals(), locals(), [obj_name])
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e)


class MonoState(object):
    _internal_state = {}

    def __new__(cls, *args, **kwargs):
        obj = super(MonoState, cls).__new__(cls)
        obj.__dict__ = cls._internal_state
        return obj


def is_pdf_url(url):
    file_type = url.split('/')[-1].split('.')[-1].lower()
    return file_type == AllowedFileType.PDF


def is_image_url(url):
    file_type = url.split('/')[-1].split('.')[-1].lower()
    return file_type in AllowedFileType.IMAGE


def is_zip_file(file_name):
    file_type = file_name.split('/')[-1].split('.')[-1].lower()
    return file_type == AllowedFileType.ZIP


class PackagePathFilter(logging.Filter):
    def filter(self, record):
        pathname = record.pathname
        abs_sys_paths = map(os.path.abspath, sys.path)
        for path in sorted(abs_sys_paths, key=len, reverse=True):  # longer paths first
            if not path.endswith(os.sep):
                path += os.sep
            if pathname.startswith(path):
                record.pathname = os.path.relpath(pathname, path).replace('/', '.').replace('\\', '.')
                break
        return True


def make_dir(target_path):
    if not os.path.exists(target_path):
        os.mkdir(target_path)


def get_logger():
    logger = logging.getLogger('gunicorn.error')
    # logger = logging.getLogger('Veronica')
    logging.basicConfig(level=logging.INFO, format='[Time: %(asctime)s] - '
                                                   '[Logger: %(name)s] - '
                                                   '[Level: %(levelname)s] - '
                                                   '[Module: %(pathname)s] - '
                                                   '[Function: %(funcName)s] - '
                                                   '%(message)s')
    logger.addFilter(PackagePathFilter())
    return logger


def get_file_size(file_path):
    try:
        size_in_bytes = os.path.getsize(file_path)

        size_in_kb = size_in_bytes / 1024.0
        size_in_mb = size_in_kb / 1024.0

        return size_in_mb

    except FileNotFoundError:
        return f"File not found: {file_path}"

    except Exception as e:
        return f"An error occurred: {str(e)}"
