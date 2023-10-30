import json
import traceback
from werkzeug.utils import secure_filename
import os
import requests
from pyzbar import pyzbar
from app import app
from app.constant import BarcodeDetection as BE
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
        results = []
        image_count = 1

        for file in image_data:
            data = {"barcode_detection": None}
            np_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config.INPUT_FOLDER, BE.Section.INPUT_PATH, filename)
            input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            cv2.imwrite(file_path, input_image)
            data['filename'] = filename
            lr_number = None
            try:
                if filename.split('.')[-1].lower() not in ['jpg', 'jpeg', 'pdf', 'png']:
                    raise InvalidFileException()
                image = cv2.imread(file_path)
                lr_number = self.detect_lr(image)
                data['barcode_detection'] = lr_number
                data['image_count'] = image_count

                results.append(data)
                image_count = image_count+1
            except NoImageFoundException as e:
                data['barcode_detection'] = lr_number
                data['image_count'] = image_count

                results.append(data)
                image_count = image_count+1
            except Exception as e:
                raise
        return results