import asyncio
import json
import os
from itertools import chain

import cv2
import numpy as np
import torch
from werkzeug.utils import secure_filename

from app import app, logger
from app.common.utils import MonoState
from app.constant import CertificateOfTitle
from app.service.helper.certificate_of_title_helper import COTHelper
from app.service.helper.cv_helper import CVHelper
from app.service.ocr.certificate_of_title.ocr import CertificateOfTitleOCR as OCR


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(CertificateOfTitle.ObjectDetection.YOLOV5, 'custom',
                           path=CertificateOfTitle.ObjectDetection.COT_OBJECT_DETECTION_MODEL_PATH, force_reload=True)
    model.conf = CertificateOfTitle.ObjectDetection.MODEL_CONFIDENCE
    return model


class COTDataPointExtractorV1(MonoState):
    _internal_state = {'model': model_loader()}

    def __init__(self, uuid):
        self.uuid = uuid
        self.label = CertificateOfTitle.ObjectDetection.OBJECT_LABELS
        self.cv_helper = CVHelper()
        self.cot_helper = COTHelper()
        self.ocr = OCR()
        self.ocr_method = {'title_no': self.ocr.get_title_number,
                           'vin': self.ocr.get_vin,
                           'year': self.ocr.get_year,
                           'make': self.ocr.get_make,
                           'model': self.ocr.get_model,
                           'body_style': self.ocr.get_body_style,
                           'odometer_reading': self.ocr.get_odometer_reading,
                           'issue_date': self.ocr.get_date,
                           'owner_name': self.ocr.get_owner_name,
                           'owner_address': self.ocr.get_address,
                           'lienholder_name': self.ocr.get_lien_name,
                           'lienholder_address': self.ocr.get_address,
                           'lien_date': self.ocr.get_date,
                           'document_type': self.ocr.get_doc_type,
                           'title_type': self.ocr.get_title_type,
                           'remark': self.ocr.get_remark
                           }

    async def __multiple_owner_address(self, owner_addresses):
        lien = None
        iou = await self.cv_helper.calculate_iou(x=owner_addresses[0]['bbox'], y=owner_addresses[1]['bbox'])
        if iou == 0:
            owner = owner_addresses[0] if owner_addresses[0]['bbox'][1] < owner_addresses[1]['bbox'][1] else \
                owner_addresses[1]
            lien = owner_addresses[0] if owner_addresses[0]['bbox'][1] > owner_addresses[1]['bbox'][1] else \
                owner_addresses[1]
        else:
            owner = owner_addresses[0] if owner_addresses[0]['score'] > owner_addresses[1]['score'] else \
                owner_addresses[1]
        return owner, lien

    async def __multiple_title_type(self, title_types):
        for title_type in title_types:
            temp = title_types.copy()
            temp.remove(title_type)
            for i in temp:
                iou = await self.cv_helper.calculate_iou(x=i['bbox'], y=title_type['bbox'])
                if iou >= 0.5:
                    min_conf = i if i['score'] < title_type['score'] else title_type
                    title_types.remove(min_conf)
        return title_types

    async def __get_multiple_objects(self, detected_object):
        title_types = []
        document_types = []
        owner_addresses = []
        for x in detected_object.pred[0]:
            if self.label[int(x[-1])] == 'owner_address':
                owner_addresses.append({'score': float(x[-2]), 'bbox': x[:-2].numpy()})
            elif self.label[int(x[-1])] == 'title_type':
                title_types.append({'score': float(x[-2]), 'bbox': x[:-2].numpy()})
            elif self.label[int(x[-1])] == 'document_type':
                document_types.append({'score': float(x[-2]), 'bbox': x[:-2].numpy()})
        return title_types, document_types, owner_addresses

    async def __detect_objects(self, image):
        _detected_objects = {}
        results = self.model(image)
        multiple_labels = ['title_type', 'owner_address', 'document_type']
        lien_addresses = None
        for x in results.pred[0]:
            """
            x[-1]  = predicted label 
            x[-2]  = predicted score
            x[:-2] = predicted bbox
            """
            if self.label[int(x[-1])] not in _detected_objects.keys() and self.label[int(x[-1])] not in multiple_labels:
                _detected_objects[self.label[int(x[-1])]] = {'score': float(x[-2]),
                                                            'bbox': x[:-2].numpy()}
            elif self.label[int(x[-1])] in _detected_objects.keys() and self.label[int(x[-1])] not in multiple_labels:
                max_score = _detected_objects[self.label[int(x[-1])]]['score']
                temp = {'score': float(x[-2]), 'bbox': x[:-2].numpy()}
                if temp['score'] > max_score:
                    _detected_objects[self.label[int(x[-1])]] = temp
        title_types, document_types, owner_addresses = await self.__get_multiple_objects(results)
        title_types = await self.__multiple_title_type(title_types)
        if owner_addresses:
            if len(owner_addresses) > 1:
                owner_addresses, lien_addresses = await self.__multiple_owner_address(owner_addresses)
            else:
                _detected_objects['owner_address'] = owner_addresses[0]
        if lien_addresses:
            _detected_objects['lienholder_address'] = lien_addresses
        title_types = await self.__get_sequential_objects(title_types, 'title_type')
        document_types = await self.__get_sequential_objects(document_types, 'document_type')
        detected_objects = {**title_types, **document_types, **_detected_objects}
        return detected_objects

    async def __get_sequential_objects(self, objects, label):
        i = 0
        _objects = {}
        for i_object in objects:
            i += 1
            _objects[label + str(i)] = i_object
        return _objects

    async def __extract_data_by_label(self, image):
        detected_objects = await self.__detect_objects(image)
        object_extraction_coroutines = [
            self.cv_helper.get_object(image, coordinates=detected_object['bbox'], label=label) for
            label, detected_object in detected_objects.items()]
        extracted_objects = await asyncio.gather(*object_extraction_coroutines)

        if len(extracted_objects) > 0:
            skew_angle = await self.cot_helper.get_skew_angel(extracted_objects)
            logger.info(f'Request ID: [{self.uuid}] found skew angle:[{skew_angle}]')
            if skew_angle >= 5 or skew_angle <= -5:
                logger.info(f'Request ID: [{self.uuid}] fixing image skew with an angle of:[{skew_angle}]')
                image = await self.cv_helper.fix_skew(image, skew_angle)
                detected_objects = await self.__detect_objects(image)
                object_extraction_coroutines = [
                    self.cv_helper.get_object(image, coordinates=detected_object['bbox'], label=label) for
                    label, detected_object in detected_objects.items()]
                extracted_objects = await asyncio.gather(*object_extraction_coroutines)

        extracted_objects_with_labels = dict()
        for i in extracted_objects:
            extracted_objects_with_labels[i['label']] = i['detected_object']

        object_extraction_coroutines = [self.__get_text_from_object(label, detected_object) for label, detected_object
                                        in extracted_objects_with_labels.items()]
        extracted_data_by_label = await asyncio.gather(*object_extraction_coroutines)
        return extracted_data_by_label

    async def __get_text_from_object(self, label, detected_object):
        if label.startswith('title_type'):
            text = await self.ocr_method['title_type'](detected_object)
        elif label.startswith('document_type'):
            text = await self.ocr_method['document_type'](detected_object)
        else:
            text = await self.ocr_method[label](detected_object)
        return [label, text]

    async def __get_all_title_types(self, extracted_data, label):
        _list = []
        for data in extracted_data:
            if data[0].startswith(label) and data[1] not in _list:
                _list.append(data[1])
        return [label, list(chain(*_list))]

    async def extract(self, file):
        data = {'certificate_of_title': None}
        np_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config.INPUT_FOLDER, filename)
        input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        cv2.imwrite(file_path, input_image)

        results_dict = dict(zip(self.label.values(), [None] * len(self.label.values())))
        # results_dict.pop('remark')
        image = await self.cv_helper.automatic_enhancement(image=input_image, clip_hist_percent=2)

        extracted_data_by_label = await self.__extract_data_by_label(image)

        if len(extracted_data_by_label) > 0:
            title_data = await self.__get_all_title_types(extracted_data_by_label, 'title_type')
            document_data = await self.__get_all_title_types(extracted_data_by_label, 'document_type')
            _extracted_data = [data for data in extracted_data_by_label if
                              not data[0].startswith('title_type') or data[0].startswith('document_type')]
            extracted_data = list(chain([title_data], [document_data], _extracted_data))
            results = {**results_dict, **dict(extracted_data)}
            data['filename'] = filename
            data['certificate_of_title'] = json.dumps(results, skipkeys=True, allow_nan=True, indent=6,
                                                      separators=("\n", " : "))
        logger.info(f'Request ID: [{self.uuid}] Response: {data}')
        return data
