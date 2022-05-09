import os

import cv2
import numpy as np
import pytesseract
from app.constant import OCRConfig
from app.service.helper.parser import parse_title_number, parse_vin, parse_year, parse_make, parse_model

pytesseract.pytesseract.tesseract_cmd = os.getenv('Tesseract_PATH')


class CertificateOfTitleOCR():
    def _apply_preprocessing(self, image):
        h, w, c = image.shape
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
        # stack = np.vstack((image, blured1, blured2, normed, image))
        image = cv2.erode(image, np.ones((3, 3), np.uint8))
        image = cv2.dilate(image, np.ones((2, 2), np.uint8))
        return image

    def get_title_number(self, image):
        pre_image = self._apply_preprocessing(image)
        dilate_image = cv2.dilate(pre_image, np.ones((2, 2), np.uint8))
        text = pytesseract.image_to_string(dilate_image, config=OCRConfig.CertificateOfTitle.TITLE_NO, lang='eng')
        text = parse_title_number(text)
        if not text:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_NO, lang='eng')
            text = parse_title_number(text)
        return text

    def get_vin(self, image):
        pre_image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(pre_image, config=OCRConfig.CertificateOfTitle.VIN, lang='eng')
        text = parse_vin(text)
        if not text:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.VIN, lang='eng')
            text = parse_vin(text)
        return text

    def get_year(self, image):
        pre_image = self._apply_preprocessing(image)
        dilate_image = cv2.dilate(pre_image, np.ones((2, 2), np.uint8))
        text = pytesseract.image_to_string(dilate_image, config=OCRConfig.CertificateOfTitle.YEAR, lang='eng')
        if not text:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.YEAR, lang='eng')
        return parse_year(text)
    
    def get_make(self, image):
        makes = {'LAND': 'LAND ROVER', 'ASTON': 'ASTON MARTIN'}
        pre_image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(pre_image, config=OCRConfig.CertificateOfTitle.MAKE, lang='eng')
        if not text:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.MAKE, lang='eng')
        parsed_text = parse_make(text)
        return makes[parsed_text] if parsed_text in makes else parsed_text
    
    def get_model(self, image):
        models = {'RANGE': 'RANGE ROVER', 'ASTON': 'ASTON MARTIN', 'LAND': 'LAND ROVER'}
        pre_image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(pre_image, config=OCRConfig.CertificateOfTitle.MODEL, lang='eng')
        if not text:
            text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.MODEL, lang='eng')
        parsed_text = parse_model(text)
        return models[parsed_text] if parsed_text in models else parsed_text
    
    def get_body_style(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.BODY_STYLE, lang='eng')
        return text
    
    def get_odometer_reading(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ODOMETER, lang='eng')
        return text
    
    def get_owner_name(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return text
    
    def get_owner_address(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ADDRESS, lang='eng')
        return text
    
    def get_lien_name(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.NAME, lang='eng')
        return text
    
    def get_lien_address(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.ADDRESS, lang='eng')
        return text
    
    def get_lien_date(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DATE, lang='eng')
        return text
    
    def get_doc_type(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DOCUMENT_TYPE, lang='eng')
        return text
    
    def get_title_type(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.TITLE_TYPE, lang='eng')
        return text

    def get_issue_date(self, image):
        image = self._apply_preprocessing(image)
        text = pytesseract.image_to_string(image, config=OCRConfig.CertificateOfTitle.DATE, lang='eng')
        return text

