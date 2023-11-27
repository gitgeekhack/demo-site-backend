import copy
import boto3
from PIL import Image
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

    def __get_line_blocks(self, response):
        word_blocks = []
        for block in response['Blocks']:
            if block['BlockType'] == 'LINE':
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
        word_blocks = self.__get_word_blocks(response)
        line_blocks = self.__get_line_blocks(response)

        extracted_texts = {}
        for obj in detected_objects:
            normalized_bbox = self.__normalize_bbox(detected_objects[obj], height, width)
            detected_objects[obj] = normalized_bbox

            text_blocks = line_blocks if obj in ['owner_address', 'lienholder_address'] else word_blocks
            text = []
            for block in text_blocks:
                overlap_score = self.__coinciding_bboxes_iou(block['bbox'], normalized_bbox)
                if overlap_score >= 0.6:
                    text.append(block['Text'])
            extracted_texts[obj] = '\n'.join(text) if obj in ['owner_address', 'lienholder_address'] else ' '.join(text)

        return extracted_texts
