import asyncio

import cv2
import numpy as np
import torch

from app import logger
from app.common.utils import MonoState
from app.service.helper.file_downloader import get_file_stream
from app.constant import DrivingLicense
from app.service.helper.cv_helper import CVHelper
from app.service.ocr import OCRDrivingLicense as OCR


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(DrivingLicense.ObjectDetection.YOLOV5, 'custom',
                           path=DrivingLicense.ObjectDetection.DL_OBJECT_DETECTION_MODEL_PATH)
    model.conf = DrivingLicense.ObjectDetection.MODEL_CONFIDENCE
    return model


class DLDataPointExtractorV1(MonoState):
    _internal_state = {'model': model_loader()}

    def __init__(self, uuid):
        self.uuid = uuid
        self.label = DrivingLicense.ObjectDetection.OBJECT_LABELS
        self.cv_helper = CVHelper()
        self.ocr = OCR(uuid)
        self.ocr_method = {'address': self.ocr.get_address,
                           'date_of_birth': self.ocr.get_date,
                           'gender': self.ocr.get_gender,
                           'license_number': self.ocr.get_license,
                           'name': self.ocr.get_name}

    async def __detect_objects(self, image):
        detected_objects = {}
        results = self.model(image)

        for x in results.pred[0]:
            """
            x[-1]  = predicted label 
            x[-2]  = predicted score
            x[:-2] = predicted bbox
            """
            if self.label[int(x[-1])] not in detected_objects.keys():
                detected_objects[self.label[int(x[-1])]] = {'score': float(x[-2]),
                                                            'bbox': x[:-2].numpy()}
            else:
                max_score = detected_objects[self.label[int(x[-1])]]['score']
                temp = {'score': float(x[-2]),
                        'bbox': x[:-2].numpy()}
                if temp['score'] > max_score:
                    detected_objects[self.label[int(x[-1])]] = temp
        return detected_objects

    async def __get_text_from_object(self, label, detected_object):
        text = await self.ocr_method[label](detected_object)
        return label, text

    async def extract(self, file):
        data = {"driving_license": None}
        np_array = np.asarray(bytearray(file.read()), dtype=np.uint8)
        input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        results_dict = dict(zip(self.label.values(), [None] * len(self.label.values())))
        detected_objects = await self.__detect_objects(input_image)
        object_extraction_coroutines = [
            self.cv_helper.get_object(input_image,
                                      coordinates=detected_object['bbox'], label=label) for label, detected_object in
            detected_objects.items()]
        extracted_objects = await asyncio.gather(*object_extraction_coroutines)
        if len(extracted_objects) > 0:
            _skew_finding_objects = []
            _skew_finding_objects.append(extracted_objects[0])
            _skew_finding_objects.extend(extracted_objects[2:])
            skew_angle = await self.cv_helper.get_skew_angel(_skew_finding_objects)
            print(f'Request ID: [{self.uuid}] found skew angle:[{skew_angle}]')
            if skew_angle >= 5 or skew_angle <= -5:
                print(f'Request ID: [{self.uuid}] fixing image skew with an angle of:[{skew_angle}]')
                input_image = await self.cv_helper.fix_skew(input_image, skew_angle)
                detected_objects = await self.__detect_objects(input_image)
                object_extraction_coroutines = [
                    self.cv_helper.get_object(input_image,
                                              coordinates=detected_object['bbox'], label=label) for
                    label, detected_object in
                    detected_objects.items()]
                extracted_objects = await asyncio.gather(*object_extraction_coroutines)

        extracted_objects_dict = {}
        for i in extracted_objects:
            extracted_objects_dict[i['label']] = i['detected_object']
        object_extraction_coroutines = [self.__get_text_from_object(label, detected_object) \
                                        for label, detected_object in extracted_objects_dict.items()]
        extracted_data = await asyncio.gather(*object_extraction_coroutines)
        if len(detected_objects.items()) > 0:
            data['driving_license'] = results_dict | dict(extracted_data)
        print(f'Request ID: [{self.uuid}] Response: {data}')
        return data
