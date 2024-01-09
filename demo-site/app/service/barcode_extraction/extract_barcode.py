import os
import traceback
from pyzbar import pyzbar
from app import logger
from app.constant import USER_DATA_PATH
from app.business_rule_exception import NoImageFoundException, InvalidFileException
from app.service.helper.image_helper import ImageHelper
import cv2
import numpy as np


class BarcodeExtraction:
    def __init__(self, uuid):
        self.uuid = uuid

    def detection(self, image):
        barcodes = pyzbar.decode(image)
        barcodeData = []
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y + 20), (x + 20, y), (0, 0, 200), 2)
            barcodeData.append(barcode.data.decode("utf-8"))
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

    def extract(self, image_data):
        data = []

        for file in image_data:
            filename = file.filename
            file_path = os.path.join(USER_DATA_PATH, filename)
            try:
                image = cv2.imread(file_path)
                lr_number = self.detect_lr(image)
                if len(lr_number) == 0:
                    return 'No Code'
                data = lr_number
            except Exception as e:
                logger.error('%s -> %s' % (e, traceback.format_exc()))
                data = 500
        return data
