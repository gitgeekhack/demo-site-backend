import asyncio
import json
import os
from itertools import chain
import traceback
import cv2
import numpy as np
import pandas as pd
import torch
from werkzeug.utils import secure_filename

from app import app, logger
from app.common.utils import MonoState
from app.constant import CertificateOfTitle
from app.service.helper.certificate_of_title_helper import COTHelper
from app.service.helper.textract import TextractHelper
from app.service.helper.cv_helper import CVHelper
from app.service.ocr.certificate_of_title.ocr import CertificateOfTitleOCR as OCR
from app.service.helper.certificate_of_title_parser import parse_title_number, parse_vin, parse_year, parse_make, \
    parse_model, parse_body_style, parse_owner_name, parse_lien_name, parse_odometer_reading, \
    parse_doc_type, parse_title_type, parse_remarks, parse_issue_date

pd.options.mode.chained_assignment = None


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(CertificateOfTitle.ObjectDetection.YOLOV5, 'custom',
                           path=CertificateOfTitle.ObjectDetection.COT_OBJECT_DETECTION_MODEL_PATH)
    model.conf = CertificateOfTitle.ObjectDetection.MODEL_CONFIDENCE
    return model


class COTDataPointExtractorV1(MonoState):
    _internal_state = {'model': model_loader()}

    def __init__(self, uuid):
        self.uuid = uuid
        self.label = CertificateOfTitle.ObjectDetection.OBJECT_LABELS
        self.section = CertificateOfTitle.Sections
        self.response_key = CertificateOfTitle.ResponseKeys
        self.cv_helper = CVHelper()
        self.cot_helper = COTHelper()
        self.ocr = OCR()
        self.textract_helper = TextractHelper()
        self.ocr_method = {self.response_key.TITLE_NO: parse_title_number,
                           self.response_key.VIN: parse_vin,
                           self.response_key.YEAR: parse_year,
                           self.response_key.MAKE: parse_make,
                           self.response_key.MODEL: parse_model,
                           self.response_key.BODY_STYLE: parse_body_style,
                           self.response_key.ODOMETER_READING: parse_odometer_reading,
                           self.response_key.ISSUE_DATE: parse_issue_date,
                           self.response_key.OWNER_NAME: parse_owner_name,
                           self.response_key.OWNER_ADDRESS: self.ocr.get_address,
                           self.response_key.LIENHOLDER_NAME: parse_lien_name,
                           self.response_key.LIENHOLDER_ADDRESS: self.ocr.get_address,
                           self.response_key.LIEN_DATE: parse_issue_date,
                           self.response_key.DOCUMENT_TYPE: parse_doc_type,
                           self.response_key.TITLE_TYPE: parse_title_type,
                           self.response_key.REMARK: parse_remarks
                           }

    async def __get_owner_lien_address(self, owner_addresses):
        lien = None
        iou = await self.cv_helper.calculate_iou(x=owner_addresses[0]['bbox'], y=owner_addresses[1]['bbox'])
        if iou == 0:
            owner, lien = (owner_addresses[0], owner_addresses[1]) if owner_addresses[0]['bbox'][1] < \
                                                                      owner_addresses[1]['bbox'][1] else (
                owner_addresses[1], owner_addresses[0])
        else:
            owner = owner_addresses[0] if owner_addresses[0]['score'] > owner_addresses[1]['score'] else \
                owner_addresses[1]
        return owner, lien

    async def __filter_title_type(self, title_types):
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
            score = float(x[-2])
            bbox = x[:-2].numpy()
            if self.label[int(x[-1])] == self.response_key.OWNER_ADDRESS:
                owner_addresses.append({'score': score, 'bbox': bbox})
            elif self.label[int(x[-1])] == self.response_key.TITLE_TYPE and score > CertificateOfTitle.VAL_SCORE:
                title_types.append({'score': float(x[-2]), 'bbox': x[:-2].numpy()})
            elif self.label[int(x[-1])] == self.response_key.DOCUMENT_TYPE and score > CertificateOfTitle.VAL_SCORE:
                document_types.append({'score': float(x[-2]), 'bbox': x[:-2].numpy()})
        return title_types, document_types, owner_addresses

    async def __detect_objects(self, image):
        _detected_objects = {}
        results = self.model(image)
        lien_addresses = None
        for x in results.pred[0]:
            """
            x[-1]  = predicted label 
            x[-2]  = predicted score
            x[:-2] = predicted bbox
            """
            if self.label[int(x[-1])] not in _detected_objects.keys() and self.label[
                int(x[-1])] not in self.section.MULTIPLE_LABELS_OBJECT:
                _detected_objects[self.label[int(x[-1])]] = {'score': float(x[-2]),
                                                             'bbox': x[:-2].numpy()}
            elif self.label[int(x[-1])] in _detected_objects.keys() and self.label[
                int(x[-1])] not in self.section.MULTIPLE_LABELS_OBJECT:
                max_score = _detected_objects[self.label[int(x[-1])]]['score']
                temp = {'score': float(x[-2]), 'bbox': x[:-2].numpy()}
                if temp['score'] > max_score:
                    _detected_objects[self.label[int(x[-1])]] = temp
        title_types, document_types, owner_addresses = await self.__get_multiple_objects(results)
        title_types = await self.__filter_title_type(title_types)
        if owner_addresses:
            if len(owner_addresses) > 1:
                owner_addresses, lien_addresses = await self.__get_owner_lien_address(owner_addresses)
            else:
                _detected_objects[self.response_key.OWNER_ADDRESS] = owner_addresses[0]
        if lien_addresses:
            _detected_objects[self.response_key.LIENHOLDER_ADDRESS] = lien_addresses
        title_types = await self.__put_sequence_number(title_types, self.response_key.TITLE_TYPE)
        document_types = await self.__put_sequence_number(document_types, self.response_key.DOCUMENT_TYPE)
        detected_objects = {**title_types, **document_types, **_detected_objects}
        return detected_objects

    async def __put_sequence_number(self, objects, label):
        i = 0
        _objects = {}
        for i_object in objects:
            i += 1
            _objects[label + str(i)] = i_object
        return _objects

    async def __extract_data_by_label(self, image, image_path):
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

        extracted_texts = {}
        if detected_objects:
            extracted_texts = self.textract_helper.get_text(image_path, detected_objects)

        post_process_text_extracted_coroutines = [self.__post_process_text(label, text) for label, text
                                                  in extracted_texts.items()]
        extracted_data_by_label = await asyncio.gather(*post_process_text_extracted_coroutines)

        if not extracted_data_by_label:
            extracted_data_by_label = [[self.label[i], None] for i in self.label]

        return extracted_data_by_label

    async def __post_process_text(self, label, text):
        if label.startswith(self.response_key.TITLE_TYPE):
            text = self.ocr_method[self.response_key.TITLE_TYPE](text)
        elif label.startswith(self.response_key.DOCUMENT_TYPE):
            text = self.ocr_method[self.response_key.DOCUMENT_TYPE](text)
        else:
            text = self.ocr_method[label](text)
        return [label, text]

    async def __get_unique_values(self, extracted_data, label):
        _set = set()
        for data in extracted_data:
            if data[0].startswith(label):
                if data[1]:
                    _set.add(tuple(data[1]))
        return [label, list(chain(*_set))]

    async def __update_labels(self, results):
        updated_results = {}
        for key in results:
            prev_key = key
            key = key.replace('_', ' ')
            key = key.title()
            if not results[prev_key]:
                updated_results[key] = 'NA'
            else:
                if isinstance(results[prev_key], dict):
                    updated_results[key] = await self.__update_labels(results[prev_key])
                else:
                    updated_results[key] = results[prev_key]
        return updated_results

    async def extract(self, image_data):
        final_results = []
        image_count = 1

        try:
            for file in image_data:
                data = {'certificate_of_title': None}
                np_array = np.asarray(bytearray(file.file.read()), dtype=np.uint8)
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config.INPUT_FOLDER, self.section.INPUT_PATH, filename)
                input_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                cv2.imwrite(file_path, input_image)

                results_dict = dict(zip(self.label.values(), [None] * len(self.label.values())))
                image = await self.cv_helper.automatic_enhancement(image=input_image, clip_hist_percent=2)
                image_path = os.path.join(os.getcwd(), file_path)
                extracted_data_by_label = await self.__extract_data_by_label(image, image_path)

                if len(extracted_data_by_label) > 0:
                    title_data = await self.__get_unique_values(extracted_data_by_label, self.response_key.TITLE_TYPE)
                    document_data = await self.__get_unique_values(extracted_data_by_label, self.response_key.DOCUMENT_TYPE)
                    _extracted_data = [data for data in extracted_data_by_label if
                                       not data[0].startswith((self.response_key.TITLE_TYPE, self.response_key.DOCUMENT_TYPE))]
                    extracted_data = list(chain([title_data], [document_data], _extracted_data))
                    results = {**results_dict, **dict(extracted_data)}
                    data['filename'] = filename
                    updated_results = await self.__update_labels(results)
                    data['certificate_of_title'] = updated_results

                final_results.append(data)
                image_count = image_count + 1
                logger.info(f'Request ID: [{self.uuid}] Response: {data}')
        except Exception as e:
            logger.error('%s -> %s' % (e, traceback.format_exc()))
        return final_results
