import logging
import os
import sys
import aiofiles

from app.constant import AllowedFileType, PDFAnnotationAndExtraction


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


def is_image_file(file):
    file_type = file.split('/')[-1].split('.')[-1].lower()
    return file_type in AllowedFileType.IMAGE


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


async def make_dir(target_path):
    if not os.path.exists(target_path):
        os.makedirs(target_path)


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


def is_allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


async def save_file(file_object, folder_path):
    await make_dir(folder_path)
    output_path = os.path.join(folder_path, file_object.filename)

    async with aiofiles.open(output_path, mode='wb+') as f:
        await f.write(file_object.file.read())


def get_file_from_path(filepath):
    class FileData:
        def __init__(self):
            self.filename = os.path.basename(filepath)
            self.file = open(os.path.join(os.getcwd(), 'app', filepath[1:]), 'rb')

    return FileData()
