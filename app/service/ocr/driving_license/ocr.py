import os

import cv2
import numpy as np
import pytesseract

from app.constant import OCRConfig
from app.service.helper.parser import parse_date, parse_name, parse_address, parse_license_number, parse_gender, \
    parse_height, \
    parse_weight, parse_hair_color, parse_eye_color, parse_license_class

pytesseract.pytesseract.tesseract_cmd = os.getenv('Tesseract_PATH')


class OCRDrivingLicense():
    def _apply_preprocessing(self, image):
        original = image
        h,w,c = image.shape
        if h > 640 or w > 640:
            image = cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_CUBIC)
        else:
            image = cv2.resize(image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured1 = cv2.medianBlur(image, 3)
        blured2 = cv2.medianBlur(image, 51)
        divided = np.ma.divide(blured1, blured2).data
        normed = np.uint8(255 * divided / divided.max())
        th, image = cv2.threshold(normed, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        stack = np.vstack((image, blured1, blured2, normed, image))
        image = cv2.erode(image, np.ones((3, 3), np.uint8))
        image = cv2.dilate(image, np.ones((3, 3), np.uint8))
        return image

    def _apply_red_color_mask(self, image):

        mask = cv2.inRange(image, (0, 0, 0), (60, 60, 100))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    def _apply_dark_red_color_mask(self, image):

        mask = cv2.inRange(image, (0, 0, 0), (80, 85, 98))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    def _apply_black_color_mask(self, image):

        mask = cv2.inRange(image, (0, 0, 0), (50, 50, 50))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    def _apply_gray_color_mask(self, image):

        mask = cv2.inRange(image, (30, 30, 30), (200, 160, 160))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    def _apply__dark_gray_color_mask(self, image):

        mask = cv2.inRange(image, (0, 0, 0), (140, 120, 120))
        image = 255 - mask
        kernel = np.ones((2, 2), np.uint8)
        image = cv2.dilate(image, kernel, iterations=3)
        image = cv2.erode(image, kernel, iterations=2)
        return image

    def get_address(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.ADDRESS, lang='eng')
        return parse_address(text)

    def get_name(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.NAME, lang='eng')

        return parse_name(text)

    def get_height(self, image):

        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.HEIGHT, lang='eng')
        return parse_height(text)

    def get_weight(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.WEIGHT, lang='eng')
        return parse_weight(text)

    def get_hair_color(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.HAIR_COLOR, lang='eng')
        return parse_hair_color(text)

    def get_eye_color(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.EYE_COLOR, lang='eng')
        return parse_eye_color(text)

    def get_license_class(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.LICENSE_CLASS, lang='eng')
        return parse_license_class(" " + text)

    def get_date(self, image):
        _image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(_image, config=OCRConfig.DrivingLicense.DATE, lang='eng')
        date = parse_date(text)

        if not date:
            print(f'Request ID:  Applying Color Mask:[black]')
            _image_black = self._apply_black_color_mask(image)
            text = pytesseract.image_to_string(_image_black, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            print(f'Request ID:  Applying Color Mask:[gray]')
            _image_gray = self._apply_gray_color_mask(image)
            text = pytesseract.image_to_string(_image_gray, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            print(f'Request ID:  Applying Color Mask:[dark gray]')
            _image_dark_gray = self._apply__dark_gray_color_mask(image)
            text = pytesseract.image_to_string(_image_dark_gray, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            print(f'Request ID:  Applying Color Mask:[red]')
            _image_red = self._apply_red_color_mask(image)
            text = pytesseract.image_to_string(_image_red, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        if not date:
            print(f'Request ID:  Applying Color Mask:[dark red]')
            _image_dark_red = self._apply_dark_red_color_mask(image)
            text = pytesseract.image_to_string(_image_dark_red, config=OCRConfig.DrivingLicense.DATE, lang='eng')
            date = parse_date(text)

        return date

    def get_license_number(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.LICENSE_NO, lang='eng')
        return parse_license_number(text)

    def get_gender(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.DrivingLicense.GENDER, lang='eng')
        return parse_gender(text)
