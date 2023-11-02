import copy
import os
import boto3
from PIL import Image
import pickle
import numpy as np


class TextractHelper:
    def __init__(self):
        self.client = boto3.client('textract', region_name='us-east-1')

    def get_textract_response(self, image_path):
        img = open(image_path, 'rb')
        image_bytes = bytearray(img.read())
        response = self.client.detect_document_text(Document={'Bytes': image_bytes})
        return response

    def __normalize_bbox(self, bbox, height, width):
        bbox[0] = np.float64(bbox[0] / width)
        bbox[1] = np.float64(bbox[1] / height)
        bbox[2] = np.float64(bbox[2] / width)
        bbox[3] = np.float64(bbox[3] / height)
        return bbox

    def __coinciding_bboxes_iou(self, box_a, box_b):
        """
        The method is used to find IOU of the bounding boxes
        :param box_a: Co-ordinates of the smaller bounding box
        :param box_b: Co-ordinates of the bigger bounding box
        :return: IOU for the given bounding boxes
        """
        box_a = tuple(np.array(box_a) * 1000)
        box_b = tuple(np.array(box_b) * 1000)

        x_a = max(box_a[0], box_b[0])
        y_a = max(box_a[1], box_b[1])
        x_b = min(box_a[2], box_b[2])
        y_b = min(box_a[3], box_b[3])

        intersect_area = max(0, x_b - x_a + 1) * max(0, y_b - y_a + 1)
        box_a_area = (box_a[2] - box_a[0] + 1) * (box_a[3] - box_a[1] + 1)
        iou = intersect_area / float(box_a_area)
        return iou

    def __get_word_blocks(self, response):
        word_blocks = []
        for block in response['Blocks']:
            if block['BlockType'] == 'WORD':
                word_block = copy.deepcopy(block)
                y_1, y_2, x_1, x_2 = block['Geometry']['BoundingBox']['Top'], \
                    block['Geometry']['BoundingBox']['Top'] + block['Geometry']['BoundingBox']['Height'], \
                    block['Geometry']['BoundingBox']['Left'], \
                    block['Geometry']['BoundingBox']['Left'] + block['Geometry']['BoundingBox']['Width']

                word_block['bbox'] = [x_1, y_1, x_2, y_2]
                word_blocks.append(word_block)

        return word_blocks

    def get_text(self, image_path, detected_objects):
        detected_objects = {i: list(detected_objects[i]['bbox']) for i in detected_objects}
        image = Image.open(image_path)
        width = image.size[0]
        height = image.size[1]

        response = self.get_textract_response(image_path)
        # response = pickle.load(open('res2.pkl', 'rb'))
        word_blocks = self.__get_word_blocks(response)

        extracted_texts = {}
        for obj in detected_objects:
            normalized_bbox = self.__normalize_bbox(detected_objects[obj], height, width)
            detected_objects[obj] = normalized_bbox

            text = []
            for block in word_blocks:
                overlap_score = self.__coinciding_bboxes_iou(block['bbox'], normalized_bbox)
                if overlap_score >= 0.6:
                    text.append(block['Text'])
            extracted_texts[obj] = ' '.join(text)

        return extracted_texts



# obj = TextractHelper()
# detected_objects = {'title_no': [423.35104, 83.999855, 543.1073, 117.46348],
#                    'model': [273.77866, 88.24867, 337.96762, 114.67835],
#                    'body_style': [335.8979, 86.90511, 418.70792, 117.98486],
#                    'make': [224.7462, 88.39578, 269.36188, 115.635544],
#                    'year': [182.43637, 89.36805, 224.74193, 116.45314],
#                    'issue_date': [32.918015, 114.9484, 120.03333, 140.91197],
#                    'odometer_reading': [121.361206, 114.48635, 194.133, 140.04453],
#                    'owners': [35.82526, 165.62361, 200.2895, 200.9949],
#                    'owner_address': [41.74136, 196.65353, 217.40897, 228.79964]}
# image_path = '/home/nirav/PycharmProjects/demo-site-backend/app/static/certificate_of_title/input_images/nevada_front_0.png'


# print(obj.get_text(image_path, detected_objects))
