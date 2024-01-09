import os
import traceback

import cv2
import numpy as np
import torch

from app import logger
from app.common.utils import MonoState
from app.common.utils import make_dir
from app.constant import CarDamageDetection, USER_DATA_PATH
from app.service.helper.cv_helper import Annotator


def model_loader():
    torch.hub._validate_not_a_forked_repo = lambda a, b, c: True
    model = torch.hub.load(CarDamageDetection.Path.YOLOV5, 'custom', path=CarDamageDetection.Path.MODEL_PATH)
    model.conf = 0.49
    return model


class DamageDetector(MonoState):
    _internal_state = {'model': model_loader()}

    def __init__(self, uuid):
        self.uuid = uuid

    async def __annotate(self, image, co_ordinates, save_path):
        annotator = Annotator(image, co_ordinates)
        annotator.annotate_and_save_image(save_path)
        logger.info(f"Request ID: [{self.uuid}] Generated image/s with damage detections")

    async def __label_colour(self, key):
        color = CarDamageDetection.ColorLabels.CAR_DAMAGE[key]
        logger.info(f'Request ID: [{self.uuid}] damaged part:[{key}]found colour: [{color}]')
        return color

    async def __predict_labels(self, image_path, save_path):
        conf_labels = {}
        results = self.model(image_path)
        pred = results.pred
        all_labels = results.names
        for label_index in range(len(all_labels)):
            all_labels[label_index] = all_labels[label_index].lower().replace(' ','_')
        for p in pred:
            img_res = tuple(map(tuple, p.numpy()))
            multi_conf_labels = [[x, [0]] for x in all_labels]
            co_ordinates = [[res[:4], await self.__label_colour(all_labels[int(res[-1])])] for res in img_res]
            for label in multi_conf_labels:
                for res in img_res:
                    if all_labels[int(res[-1])] == label[0]:
                        label[1].append(int(res[4] * 100))
            for label in multi_conf_labels:
                conf_labels[label[0]] = max(label[1])
            img = cv2.imread(image_path)
            await self.__annotate(img, co_ordinates, save_path)
            logger.info(f'Request ID: [{self.uuid}] co-ordinates obtained: [{co_ordinates}]')
        return conf_labels

    async def detect(self, image_data):
        results = []

        for file_data in image_data:
            filename = file_data.filename
            input_file_path = os.path.join(USER_DATA_PATH, filename)
            output_file_path = os.path.join(USER_DATA_PATH, 'out_' + filename)
            logger.info(f"Request ID: [{self.uuid}]Input image/s received...")
            detection = await self.__predict_labels(input_file_path, output_file_path)
            out_path = os.path.join(USER_DATA_PATH, 'out_' + filename)
            results.append({'results': detection, 'file_path': out_path})

        logger.info(f'Request ID: [{self.uuid}] results obtained: [{results}]')
        return results
