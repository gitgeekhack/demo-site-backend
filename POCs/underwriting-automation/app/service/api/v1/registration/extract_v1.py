import asyncio

import cv2
import numpy as np
import torch

from app import logger
from app.common.utils import MonoState
from app.constant import Registration
from app.service.helper.cv_helper import CVHelper
from app.service.helper.file_downloader import get_file_stream
from app.service.ocr import OCRRegistrationCard as OCR


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(Registration.ObjectDetection.YOLOV5, 'custom',
                           path=Registration.ObjectDetection.REG_OBJECT_DETECTION_MODEL_PATH)
    model.conf = Registration.ObjectDetection.MODEL_CONFIDENCE
    return model


class REGDataPointExtractorV1(MonoState):
    _internal_state = {'model': model_loader()}

    def __init__(self, uuid):
        self.uuid = uuid
        self.label = Registration.ObjectDetection.OBJECT_LABELS
        self.cv_helper = CVHelper()
        self.ocr = OCR(uuid)
        self.ocr_method = {'name': self.ocr.get_owner_names,
                           'validity': self.ocr.get_validity,
                           'make': self.ocr.get_make,
                           'year': self.ocr.get_year,
                           'vin': self.ocr.get_vin,
                           'history': self.ocr.get_history,
                           }

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

    async def __get_vehicle_info(self, extracted_data):
        vehicle = dict.fromkeys(Registration.ObjectDetection.VEHICLE_DETAILS)
        for i_label in Registration.ObjectDetection.VEHICLE_DETAILS:
            if i_label in extracted_data:
                vehicle[i_label] = extracted_data[i_label]
            else:
                vehicle[i_label] = None
        return vehicle

    async def extract(self, file):
        data = {"registration": None}
        np_array = np.asarray(bytearray(file.read()), dtype=np.uint8)
        input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        detected_objects = await self.__detect_objects(input_image)
        object_extraction_coroutines = [
            self.cv_helper.get_object(input_image,
                                      coordinates=detected_object['bbox'], label=label) for label, detected_object in
            detected_objects.items()]
        extracted_objects = await asyncio.gather(*object_extraction_coroutines)
        if len(extracted_objects) > 0:
            skew_angle = await self.cv_helper.get_skew_angel(extracted_objects)
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
            result = {}
            extracted_data = dict(extracted_data)
            result['owners'] = extracted_data['name'] if 'name' in extracted_data and extracted_data['name'] else None
            result['is_valid'] = extracted_data['validity'] if 'validity' in extracted_data else None
            result['vehicle'] = await self.__get_vehicle_info(extracted_data)
            data['registration'] = result
        print(f'Request ID: [{self.uuid}] Response: {data}')

        return data
