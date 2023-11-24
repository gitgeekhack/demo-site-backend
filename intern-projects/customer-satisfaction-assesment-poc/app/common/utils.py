import os
import sys
import logging


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
    logging.basicConfig(level=logging.INFO, format='[Time: %(asctime)s] - '
                                                   '[Logger: %(name)s] - '
                                                   '[Level: %(levelname)s] - '
                                                   '[Module: %(pathname)s] - '
                                                   '[Function: %(funcName)s] - '
                                                   '%(message)s')
    logger.addFilter(PackagePathFilter())
    return logger
