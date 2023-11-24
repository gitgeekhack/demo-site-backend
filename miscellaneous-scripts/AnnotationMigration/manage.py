import logging
from logging.handlers import RotatingFileHandler
import os
import sys

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

def get_logger():
    handler = RotatingFileHandler("annotations-migration.log", maxBytes=10485760, backupCount=1000)
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('annotation-data-migration')
    # logger.propagate = False
    logger.addFilter(PackagePathFilter())
    formatter = logging.Formatter('[%(asctime)s] - '
                                  '[%(levelname)s] - '
                                  '[logger: %(name)s] - '
                                  '[module: %(pathname)s] - '
                                  '[function: %(funcName)s] - '
                                  '%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = get_logger()
def create_logger():
    logger = get_logger()
    return logger