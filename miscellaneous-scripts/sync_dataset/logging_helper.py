import logging
import os
import sys
import datetime


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
    date_time = datetime.datetime.now().strftime('%m%d%Y_%H%M')
    log_format = "[%(asctime)s] - [%(levelname)s] - [logger: %(name)s] - [module: %(pathname)s] - [function: %(funcName)s] - %(message)s"
    logging.basicConfig(filename=f'dataset_sync_{date_time}.log', level='INFO', format=log_format)
    logger = logging.getLogger('dataset-sync')
    logger.addFilter(PackagePathFilter())
    return logger


logger = get_logger()
