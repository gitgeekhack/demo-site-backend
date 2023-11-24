import asyncio

import cv2
import fitz
import numpy as np
from scipy.ndimage import interpolation as inter

from app.business_rule_exception import MissingRequiredParameterException

"""
The Object Extraction helper signifies helper class which provides necessary supporting methods used in object extraction
"""


class CVHelper:
    """Contains crop_object method which takes image and respective box dimension for detected object, crops and
    returns the image """

    async def get_object(self, target_img, coordinates, label):
        """
        Parameters:
            target_img <class 'numpy.ndarray'>: The target image which is to be cropped.
            coordinates <class 'list'>: The coordinates of the region to be cropped, a 4-element list containing
                                of x/y (x0, y0, x1, y1) pixel coordinates.
        Returns:
            cropped_img <class 'numpy.ndarray'>: The final image which is cropped with the coordinates provided.
        """
        x0, y0, x1, y1 = [int(x) for x in coordinates]
        w = target_img.shape[0]
        h = target_img.shape[1]
        padd = 0.005
        w_padd = w * padd
        h_padd = h * padd
        x0, y0 = int(x0 - w_padd), int(y0 - w_padd)
        x1, y1 = int(x1 + h_padd), int(y1 + h_padd)
        cropped_img = target_img[y0:y1, x0:x1]
        return {'detected_object': cropped_img, 'label': label}

    async def cropp_object(self, target_img):
        """
        Parameters:
            target_img <class 'numpy.ndarray'>: The target image which is to be cropped.
            coordinates <class 'list'>: The coordinates of the region to be cropped, a 4-element list containing
                                of x/y (x0, y0, x1, y1) pixel coordinates.
        Returns:
            cropped_img <class 'numpy.ndarray'>: The final image which is cropped with the coordinates provided.
        """
        h = target_img.shape[0]
        w = target_img.shape[1]
        w_padd = 0.05
        h_padd = 0.08
        new_w = int(w * w_padd)
        new_h = int(h * h_padd)

        cropped = target_img[:h - new_h, :w - new_w]

        return cropped

    async def extract_image_from_pdf(self, doc, image_list):
        if image_list[1] and image_list[5] == 'DeviceRGB':
            full_image = fitz.Pixmap(doc, image_list[0])
            mask = fitz.Pixmap(doc, image_list[1])
            covered_image = fitz.Pixmap(full_image, mask)
            np_array = np.asarray(bytearray(covered_image.tobytes()), dtype=np.uint8)
            input_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
            trans_mask = input_image[:, :, 3] == 0
            input_image[trans_mask] = [255, 255, 255, 255]
            new_img = cv2.cvtColor(input_image, cv2.COLOR_BGRA2BGR)
            return new_img

        else:
            xref = image_list[0]
            pix = fitz.Pixmap(doc, xref)
            if pix.n < 5:
                np_array = np.asarray(bytearray(pix.tobytes()), dtype=np.uint8)
                input_image = cv2.imdecode(np_array, cv2.IMREAD_UNCHANGED)
                new_img = cv2.cvtColor(input_image, cv2.COLOR_BGRA2BGR)
                return new_img

    async def calculate_iou(self, container_bbox, signature_bbox):
        x0 = max(container_bbox[0], signature_bbox[0])
        y0 = max(container_bbox[1], signature_bbox[1])
        x1 = min(container_bbox[2], signature_bbox[2])
        y1 = min(container_bbox[3], signature_bbox[3])
        inter_area = max(0, x1 - x0 + 1) * max(0, y1 - y0 + 1)
        box0_area = (container_bbox[2] - container_bbox[0] + 1) * (container_bbox[3] - container_bbox[1] + 1)
        box1_area = (signature_bbox[2] - signature_bbox[0] + 1) * (signature_bbox[3] - signature_bbox[1] + 1)
        iou = inter_area / float(box0_area + box1_area - inter_area)
        return iou

    async def __find_skew_score(self, arr, angle):
        data = inter.rotate(arr, angle, reshape=False, order=0)
        histogram = np.sum(data, axis=1)
        score = np.sum((histogram[1:] - histogram[:-1]) ** 2)
        return histogram, score

    async def __calculate_skew_angel(self, image, delta=5, limit=45):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        scores = []
        angles = np.arange(-limit, limit + delta, delta)
        for angle in angles:
            histogram, score = await self.__find_skew_score(thresh, angle)
            scores.append(score)
        best_angle = angles[scores.index(max(scores))]
        return best_angle

    async def get_skew_angel(self, extracted_objects):
        find_skew_angles = [self.__calculate_skew_angel(extracted_object['detected_object']) for
                            extracted_object
                            in
                            extracted_objects]
        skew_angles = await asyncio.gather(*find_skew_angles)
        max_skew_angle = np.max(skew_angles)
        min_skew_angle = np.min(skew_angles)
        if min_skew_angle < 0:
            skew_angle = min_skew_angle
        else:
            skew_angle = max_skew_angle

        return skew_angle

    async def fix_skew(self, image, angle):
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    async def match_template(self, template, image):
        """
        Parameters:
            template <class 'numpy.ndarray'> : The source Searched template.
            image <class 'numpy.ndarray'> : The input image where the search is running.
        Returns:
            Boolean: True if the input image matches the template, False otherwise.
        """
        if template is None:
            raise MissingRequiredParameterException('Missing Required input Template Parameter for Template Matching')
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        match = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.9
        if match.all() >= threshold:
            return True
        return False
