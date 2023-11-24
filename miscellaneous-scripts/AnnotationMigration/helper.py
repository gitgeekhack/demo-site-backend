import hashlib
import logging
import os
import sys
from configparser import ConfigParser
from io import StringIO

import xmltodict
from PyPDF2 import PdfFileReader, PdfFileWriter
from logging.handlers import RotatingFileHandler



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


class UnsuccessfulProcess(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}'


def read_properties_file(file_path):
    with open(file_path) as f:
        config = StringIO()
        config.write("[dummy_section]\n")
        config.write(f.read().replace("%", "%%"))
        config.seek(0, os.SEEK_SET)
        cp = ConfigParser()
        cp.read_file(config)
        return dict(cp.items("dummy_section"))


def generate_md5_hash(file_path):
    buf_size = 65536
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def create_split_pdf(pdf_file_path, split_dir_p, split_start, split_end):
    split_name = os.path.basename(split_dir_p)
    input_pdf = PdfFileReader(pdf_file_path, strict=False)
    output_pdf = PdfFileWriter()
    for i in range(split_start - 1, split_end):
        output_pdf.addPage(input_pdf.getPage(i))
    with open(split_dir_p + "/" + split_name + "." + os.path.basename(pdf_file_path), 'wb') as file1:
        output_pdf.write(file1)


def xml_to_dict(xml_path):
    with open(xml_path, 'r', encoding='utf-8') as file:
        my_xml = file.read()
    my_dict = xmltodict.parse(my_xml)
    return my_dict


def get_pdf_file_path(dir_p):
    for file in os.listdir(dir_p):
        if file.endswith(".pdf") or file.endswith(".PDF"):
            return os.path.join(dir_p, file)


def get_split_dirs(dir_p):
    split_dirs = []
    for file in os.listdir(dir_p):
        if os.path.isdir(dir_p + "/" + file) and file[0].isdigit():
            split_dirs.append(os.path.join(dir_p, file))
    return split_dirs


def get_project_dirs(dir_p):
    project_dirs = []
    for file in os.listdir(dir_p):
        if os.path.isdir(dir_p + "/" + file) and not (file[0].isdigit()):
            project_dirs.append(os.path.join(dir_p, file))
    return project_dirs[0] if project_dirs else None


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
