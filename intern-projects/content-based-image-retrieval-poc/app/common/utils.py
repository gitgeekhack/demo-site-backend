import logging
import os, sys
from configparser import ConfigParser
from io import StringIO
from logging.handlers import TimedRotatingFileHandler
from app.constant import ALLOWED_EXTENSIONS

INSTANCE_LOG_FOLDER_PATH = os.path.abspath(os.path.join(__file__, '..', '..', '..', 'logs'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_properties_file(file_path):
    with open(file_path) as f:
        config = StringIO()
        config.write("[dummy_section]\n")
        config.write(f.read().replace("%", "%%"))
        config.seek(0, os.SEEK_SET)
        cp = ConfigParser()
        cp.read_file(config)
        return dict(cp.items("dummy_section"))


def setup_logger():
    """Set up the global logging settings."""
    generated_files = INSTANCE_LOG_FOLDER_PATH
    all_log_filename = '{0}/all.log'.format(generated_files)
    error_log_filename = '{0}/error.log'.format(generated_files)
    make_dir(INSTANCE_LOG_FOLDER_PATH)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(LogFormatter())
    logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.handlers.RotatingFileHandler(error_log_filename, maxBytes=1000000, backupCount=100)
    handler.setLevel(logging.ERROR)
    handler.setFormatter(LogFormatter())
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.handlers.RotatingFileHandler(all_log_filename,
                                                   maxBytes=1000000,
                                                   backupCount=100)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(LogFormatter())
    logger.addHandler(handler)
    return logger


def make_dir(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


class LogFormatter(logging.Formatter):
    """."""
    date_format = '%Y-%m-%d %H:%M:%S'

    def format(self, record):
        """."""
        error_location = "%s.%s" % (record.name, record.funcName)
        line_number = "%s" % record.lineno
        location_line = error_location[:32] + ":" + line_number
        s = "%.19s [%-8s] [%-36s] %s" % (self.formatTime(record, self.date_format),
                                         record.levelname, location_line,
                                         record.getMessage())
        return s


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

def get_logger():
    logger = logging.getLogger('gunicorn.error')
    logging.basicConfig(level=logging.INFO, format='[Time: %(asctime)s] - '
                                                   '[Logger: %(name)s] - '
                                                   '[Level: %(levelname)s] - '
                                                   '[Module: %(pathname)s] - '
                                                   '[Function: %(funcName)s] - '
                                                   '%(message)s')
    # logger.addFilter(PackagePathFilter())
    return logger

