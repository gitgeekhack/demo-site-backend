from flask import current_app
from app.common.utils import file_downloader, stop_watch
from app.services.helper.pdf_helper import PDFHelper
import os


class PDFExtractor:

    @stop_watch
    def extract_first_image_from_url(self, url):
        file, name = file_downloader(url, current_app.config['TMP_STORAGE_PATH'])
        image = PDFHelper().extract_first_image(file)
        if image:
            img_name = "".join(name.split('.')[:-1]) + '.png'
            target = os.path.join(current_app.config['TMP_STORAGE_PATH'], img_name)
            image.save(target)
            success = True
            return success, img_name
        success = False
        return success, None

    @stop_watch
    def extract_first_image_from_by_file(self, file_name):
        file_path = os.path.join(current_app.config['TMP_STORAGE_PATH'], file_name)
        image = PDFHelper().extract_first_image(file_path)
        if image:
            img_name = "".join(file_name.split('.')[:-1]) + '.png'
            target = os.path.join(current_app.config['TMP_STORAGE_PATH'], img_name)
            image.save(target)
            success = True
            return success, target, img_name
        success = False
        return success, None, None