import json
import traceback

import requests
from pyzbar import pyzbar
from flask import current_app

from app.business_rule_exception import FailedToDownloadFileFromURLException, NoImageFoundException, \
    InvalidFileException
from app.constants import APIErrorMessage
from app.services.helper.image_helper import ImageHelper
from app.services.classification import Classification
from app.common.utils import file_downloader, stop_watch
import cv2

from app.services.pdf_image_extraction import PDFExtractor


class BarcodeExtraction:

    @stop_watch
    def predict_label(self, image):
        cl = Classification()
        label = cl.classify(image)
        return label

    @stop_watch
    def detection(self, image):
        barcodes = pyzbar.decode(image)
        barcodeData = None
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y + 20), (x + 20, y), (0, 0, 200), 2)
            barcodeData = barcode.data.decode("utf-8")
            barcodeData = int(barcodeData)
        return barcodeData

    def detect_lr(self, image):
        br = ImageHelper()
        lr_number = self.detection(image)
        if not lr_number:
            preprocessed_image = br.preprocess(image)
            lr_number = self.detection(preprocessed_image)
            if not lr_number:
                obj_det_image = br.object_detection(image)
                lr_number = self.detection(obj_det_image)
        return lr_number

    def get_image_from_pdf(self, file):
        success, file_path, image_name = PDFExtractor().extract_first_image_from_by_file(file)
        if success:
            return file_path, image_name
        else:
            raise NoImageFoundException(file)

    @stop_watch
    def extract_by_url(self, document_url):
        lr_number = None
        success = False
        try:
            file_path, name = file_downloader(document_url, current_app.config['TMP_STORAGE_PATH'])
            if name.split('.')[-1].lower() not in current_app.config['ALLOWED_EXT']:
                raise InvalidFileException(document_url)
            if '.pdf' in name:
                file_path, name = self.get_image_from_pdf(name)
            image = cv2.imread(file_path)
            label = self.predict_label(image)
            current_app.logger.info(f'Classification => {label}')
            if label == 'Clear':
                lr_number = self.detect_lr(image)
                if lr_number:
                    success = True
            elif label == 'Invalid':
                success = False
            else:
                pass
            return success, {
                "classified_as": label,
                "lr_number": lr_number
            }
        except NoImageFoundException as e:
            return success, {
                "classified_as": 'Invalid',
                "lr_number": lr_number
            }
        except Exception as e:
            raise
