import asyncio
import os

import cv2
import numpy as np
import torch
from werkzeug.utils import secure_filename

from app import logger, app
from app.common.utils import MonoState
from app.constant import DrivingLicense
from app.service.helper.cv_helper import CVHelper
from app.service.ocr.driving_license.ocr import OCRDrivingLicense as OCR


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(DrivingLicense.ObjectDetection.YOLOV5, 'custom',
                           path=DrivingLicense.ObjectDetection.DL_OBJECT_DETECTION_MODEL_PATH, force_reload=True)
    model.conf = DrivingLicense.ObjectDetection.MODEL_CONFIDENCE
    return model


class DLDataPointExtractorV1(MonoState):
    _internal_state = {'model': model_loader()}

    def __init__(self, uuid):
        self.uuid = uuid
        self.label = DrivingLicense.ObjectDetection.OBJECT_LABELS
        self.cv_helper = CVHelper()
        self.ocr = OCR()
        self.ocr_method = {'address': self.ocr.get_address,
                           'date': self.ocr.get_date,
                           'gender': self.ocr.get_gender,
                           'license_number': self.ocr.get_license_number,
                           'name': self.ocr.get_name,
                           'eye_color': self.ocr.get_eye_color,
                           'hair_color': self.ocr.get_hair_color,
                           'license_class': self.ocr.get_license_class,
                           'height': self.ocr.get_height,
                           'weight': self.ocr.get_weight
                           }

    async def __multiple_dates(self, dates):
        for date in dates:
            temp = dates.copy()
            temp.remove(date)
            for x in temp:
                iou = await self.cv_helper.calculate_iou(x=x['bbox'], y=date['bbox'])
                if iou >= 0.5:
                    max_conf = x if x['score'] < date['score'] else date
                    dates.remove(max_conf)
        return dates

    async def __detect_objects(self, image):
        detected_objects = {}
        results = self.model(image)
        dates = []

        for x in results.pred[0]:
            """
            x[-1]  = predicted label 
            x[-2]  = predicted score
            x[:-2] = predicted bbox
            """
            if self.label[int(x[-1])] not in detected_objects.keys() and self.label[int(x[-1])] != 'date':
                detected_objects[self.label[int(x[-1])]] = {'score': float(x[-2]),
                                                            'bbox': x[:-2].numpy()}
            elif self.label[int(x[-1])] == 'date':
                dates.append({'score': float(x[-2]), 'bbox': x[:-2].numpy()})
            else:
                max_score = detected_objects[self.label[int(x[-1])]]['score']
                temp = {'score': float(x[-2]),
                        'bbox': x[:-2].numpy()}
                if temp['score'] > max_score:
                    detected_objects[self.label[int(x[-1])]] = temp
        dates = await self.__multiple_dates(dates)
        i = 0
        for date in dates:
            i += 1
            detected_objects['date' + str(i)] = date
        return detected_objects

    async def __get_text_from_object(self, label, detected_object):
        if label.startswith('date'):
            text = self.ocr_method['date'](detected_object)
        else:
            text = self.ocr_method[label](detected_object)
        return label, text

    async def __extract_objects(self, image):
        detected_objects = await self.__detect_objects(image)
        dates_coroutines = None
        object_extraction_coroutines = [
            self.cv_helper.get_object(image,
                                      coordinates=detected_object['bbox'], label=label) for label, detected_object in
            detected_objects.items() if label != 'dates']
        for label, detected_object in detected_objects.items():
            if label == 'dates':
                dates_coroutines = [self.cv_helper.get_object(image, coordinates=x['bbox'], label=label) for x in
                                    detected_object]
        if dates_coroutines:
            object_extraction_coroutines.extend(dates_coroutines)
        extracted_objects = await asyncio.gather(*object_extraction_coroutines)
        if len(extracted_objects) > 0:
            _skew_finding_objects = []
            _skew_finding_objects.append(extracted_objects[0])
            _skew_finding_objects.extend(extracted_objects[2:])
            skew_angle = await self.cv_helper.get_skew_angel(_skew_finding_objects)
            logger.info(f'Request ID: [{self.uuid}] found skew angle:[{skew_angle}]')
            if skew_angle >= 5 or skew_angle <= -5:
                logger.info(f'Request ID: [{self.uuid}] fixing image skew with an angle of:[{skew_angle}]')
                image = await self.cv_helper.fix_skew(image, skew_angle)
                detected_objects = await self.__detect_objects(image)
                object_extraction_coroutines = [
                    self.cv_helper.get_object(image,
                                              coordinates=detected_object['bbox'], label=label) for
                    label, detected_object in
                    detected_objects.items()]
                extracted_objects = await asyncio.gather(*object_extraction_coroutines)
        return extracted_objects, detected_objects

    async def extract(self, file):
        data = {"driving_license": None}
        np_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config.TEMP_FOLDER, filename)
        input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        cv2.imwrite(file_path, input_image)

        results_dict = dict(zip(self.label.values(), [None] * len(self.label.values())))
        image = await self.cv_helper.automatic_enhancement(image=input_image, clip_hist_percent=2)

        extracted_objects, detected_objects = await self.__extract_objects(image)
        extracted_objects_dict = dict()

        for i in extracted_objects:
            extracted_objects_dict[i['label']] = i['detected_object']
        object_extraction_coroutines = [self.__get_text_from_object(label, detected_object) for label, detected_object
                                        in extracted_objects_dict.items()]
        extracted_data = await asyncio.gather(*object_extraction_coroutines)

        if len(detected_objects.items()) > 0:
            date = [y for x, y in extracted_data if x.startswith('date')]
            shared_keys = results_dict.keys() & dict(extracted_data).keys()
            data['driving_license'] = {k: dict(extracted_data)[k] for k in shared_keys}
            data['driving_license']['date'] = ', '.join(map(str, date))
            data['driving_license']['filename'] = filename
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')

        return data
